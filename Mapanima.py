#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
st.set_page_config(page_title="Mapanima - Geovisor Étnico", layout="wide")

# --- Ajuste visual para reducir espacio en blanco del mapa ---
st.markdown("""
<style>
    .element-container:has(> iframe) {
        height: 650px !important;
        margin-bottom: 0rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Banner superior ---
st.image("GEOVISOR.png", use_container_width=True)

import geopandas as gpd
import pandas as pd
from io import BytesIO
import zipfile
import tempfile
import os
import folium
from streamlit_folium import st_folium

st.title("🗺️ Mapanima - Geovisor Étnico")

with st.expander("🧭 ¿Qué es Mapanima?"):
    st.markdown(
        """
        <div style='font-size:16px; text-align:justify;'>
        <strong>Mapanima</strong> nace de la fusión entre “mapa” y “ánima”, evocando no solo la representación gráfica de un territorio, sino su alma, su energía viva.<br><br>
        Este nombre es una metáfora del territorio étnico, entendido no como una extensión vacía delimitada por coordenadas, sino como un espacio sagrado, habitado, sentido y narrado por los pueblos originarios.<br><br>
        <strong>Mapanima</strong> honra la cosmovisión indígena donde la tierra tiene memoria, espíritu y dignidad.
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Función para cargar SHP desde un .zip ---
def cargar_shapefile_zip(uploaded_zip):
    if not uploaded_zip:
        return None
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
            shp_path = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".shp")]
            if not shp_path:
                st.error("No se encontró ningún archivo .shp en el .zip")
                return None
            return gpd.read_file(shp_path[0])

# --- Subir capa unificada desde la barra lateral ---
st.sidebar.header("📂 Cargar capa")
zip_territorios = st.sidebar.file_uploader("Sube archivo .zip con SHP unificado", type="zip")
gdf_total = cargar_shapefile_zip(zip_territorios)

if gdf_total is not None:
    # Normalizar campos
    gdf_total['etapa'] = gdf_total['etapa'].str.lower()
    gdf_total['estado_act'] = gdf_total['estado_act'].str.strip()
    gdf_total['cn_ci'] = gdf_total['cn_ci'].str.lower()

    # --- Filtros en la barra lateral ---
    st.sidebar.header("🎯 Filtros")

    etapas = gdf_total['etapa'].dropna().unique().tolist()
    etapa_sel = st.sidebar.multiselect("Filtrar por etapa", sorted(etapas))

    estados = gdf_total['estado_act'].dropna().unique().tolist()
    estado_sel = st.sidebar.multiselect("Filtrar por estado del caso", sorted(estados))

    tipos = gdf_total['cn_ci'].dropna().unique().tolist()
    tipo_sel = st.sidebar.multiselect("Filtrar por tipo de territorio", sorted(tipos))

    departamentos = gdf_total['departamen'].dropna().unique().tolist()
    depto_sel = st.sidebar.multiselect("Filtrar por departamento", sorted(departamentos))

    id_buscar = st.sidebar.text_input("🔍 Buscar por ID (id_rtdaf)")
    nombre_buscar = st.sidebar.text_input("🔍 Buscar por nombre (nom_terr)")

    # --- Opciones de rendimiento ---
    st.sidebar.header("⚙️ Rendimiento")
    usar_simplify = st.sidebar.checkbox("Simplificar geometría", value=True)
    tolerancia = st.sidebar.slider("Nivel de simplificación", 0.00001, 0.001, 0.0001, step=0.00001, format="%.5f")
    st.sidebar.caption(f"Valor actual: `{tolerancia}`")

    # --- Estado del visor ---
    if "mostrar_mapa" not in st.session_state:
        st.session_state["mostrar_mapa"] = False

    col_botones = st.sidebar.columns(2)
    with col_botones[0]:
        if st.button("🧭 Aplicar filtros y mostrar mapa"):
            st.session_state["mostrar_mapa"] = True
    with col_botones[1]:
        if st.button("🔄 Reiniciar visor"):
            st.session_state["mostrar_mapa"] = False
            st.rerun()

    # --- Generación del mapa con filtros ---
    if st.session_state["mostrar_mapa"]:
        gdf_filtrado = gdf_total.copy()
        if etapa_sel:
            gdf_filtrado = gdf_filtrado[gdf_filtrado["etapa"].isin(etapa_sel)]
        if estado_sel:
            gdf_filtrado = gdf_filtrado[gdf_filtrado["estado_act"].isin(estado_sel)]
        if tipo_sel:
            gdf_filtrado = gdf_filtrado[gdf_filtrado["cn_ci"].isin(tipo_sel)]
        if depto_sel:
            gdf_filtrado = gdf_filtrado[gdf_filtrado["departamen"].isin(depto_sel)]
        if id_buscar:
            gdf_filtrado = gdf_filtrado[gdf_filtrado["id_rtdaf"].astype(str).str.contains(id_buscar)]
        if nombre_buscar:
            gdf_filtrado = gdf_filtrado[gdf_filtrado["nom_terr"].str.lower().str.contains(nombre_buscar.lower())]

        if usar_simplify:
            gdf_filtrado["geometry"] = gdf_filtrado["geometry"].simplify(tolerancia, preserve_topology=True)

        st.subheader("🗺️ Mapa filtrado")

        if not gdf_filtrado.empty:
            # Reproyectar a WGS84 para folium
            gdf_filtrado = gdf_filtrado.to_crs(epsg=4326)

            # Calcular centro y límites
            bounds = gdf_filtrado.total_bounds
            centro_lat = (bounds[1] + bounds[3]) / 2
            centro_lon = (bounds[0] + bounds[2]) / 2

            m = folium.Map(location=[centro_lat, centro_lon], zoom_start=10, tiles="CartoDB positron")

            def style_function_by_tipo(feature):
                tipo = feature["properties"]["cn_ci"]
                color = "#228B22" if tipo == "ci" else "#8B4513"
                return {
                    "fillColor": color,
                    "color": color,
                    "weight": 1,
                    "fillOpacity": 0.6
                }

            geojson = folium.GeoJson(
                gdf_filtrado,
                style_function=style_function_by_tipo,
                tooltip=folium.GeoJsonTooltip(
                    fields=["id_rtdaf", "nom_terr", "etnia", "departamen", "municipio", "etapa", "estado_act"],
                    aliases=["ID:", "Territorio:", "Etnia:", "Departamento:", "Municipio:", "Etapa:", "Estado:"],
                    localize=True
                )
            ).add_to(m)

            m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

            st_data = st_folium(m, width=1200, height=600)

            # --- Mostrar tabla con resultados ---
            st.subheader("📋 Resultados filtrados")
            st.dataframe(gdf_filtrado.drop(columns="geometry"))

            # --- Botón para descargar CSV ---
            csv = gdf_filtrado.drop(columns="geometry").to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Descargar CSV de resultados",
                data=csv,
                file_name="resultados_filtrados.csv",
                mime="text/csv"
            )

            # --- Botón para descargar Shapefile como ZIP ---
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "shapefile_filtrado.zip")
                shp_base = os.path.join(tmpdir, "shapefile_filtrado")
                gdf_filtrado.to_file(shp_base + ".shp", driver="ESRI Shapefile", encoding="utf-8")
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
                        fpath = shp_base + ext
                        if os.path.exists(fpath):
                            zipf.write(fpath, arcname="shapefile_filtrado" + ext)
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Descargar Shapefile filtrado (.zip)",
                        data=f,
                        file_name="shapefile_filtrado.zip",
                        mime="application/zip"
                    )

            # --- Exportar mapa a HTML ---
            if st.sidebar.button("💾 Exportar mapa a HTML"):
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmpfile:
                    m.save(tmpfile.name)
                    st.success("✅ Mapa exportado correctamente.")
                    with open(tmpfile.name, "rb") as f:
                        st.download_button(
                            label="⬇️ Descargar HTML del mapa",
                            data=f,
                            file_name="mapa_etnico_filtrado.html",
                            mime="text/html"
                        )

        else:
            st.warning("⚠️ No se encontraron resultados con los filtros aplicados.")

# --- Créditos al pie ---
st.markdown("""---""")
st.markdown(
    "<div style='text-align: center; font-size: 14px;'>"
    "Realizado por <strong>Ing. Luis Miguel Guerrero</strong> — DAE — "
    "<a href='mailto:luis.guerrero@urt.gov.co'>luis.guerrero@urt.gov.co</a>"
    "</div>",
    unsafe_allow_html=True
)

