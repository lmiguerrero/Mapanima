#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
st.set_page_config(page_title="Mapanima - Geovisor Étnico", layout="wide")

# --- Estilo visual personalizado ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0fff0;
    }
    div.stButton > button:first-child {
        background-color: #2e6f57;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5em 1em;
    }
    </style>
    """,
    unsafe_allow_html=True
)

import geopandas as gpd
import pandas as pd
from io import BytesIO
import zipfile
import tempfile
import os
import folium
from streamlit_folium import st_folium

st.markdown(
    "<h1 style='text-align: center; color: #2e6f57;'>🗺️ Mapanima - Geovisor Étnico</h1>",
    unsafe_allow_html=True
)
st.image("GEOVISOR.png", use_container_width=True)

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
    st.sidebar.markdown("---")
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
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Rendimiento")
    usar_simplify = st.sidebar.checkbox("Simplificar geometría", value=True)
    tolerancia = st.sidebar.slider("Nivel de simplificación", 0.00001, 0.001, 0.0001, step=0.00001, format="%.5f")
    st.sidebar.caption(f"Valor actual: `{tolerancia}`")

    # --- Estado del visor ---
    st.sidebar.markdown("---")
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
            m = folium.Map(location=[4.5, -74.1], zoom_start=5, tiles="CartoDB positron")

            def style_function_by_tipo(feature):
                tipo = feature["properties"]["cn_ci"]
                color = "#228B22" if tipo == "ci" else "#8B4513"
                return {
                    "fillColor": color,
                    "color": color,
                    "weight": 1,
                    "fillOpacity": 0.6
                }

            folium.GeoJson(
                gdf_filtrado,
                style_function=style_function_by_tipo,
                tooltip=folium.GeoJsonTooltip(
                    fields=["id_rtdaf", "nom_terr", "etnia", "departamen", "municipio", "etapa", "estado_act"],
                    aliases=["ID:", "Territorio:", "Etnia:", "Departamento:", "Municipio:", "Etapa:", "Estado:"],
                    localize=True
                )
            ).add_to(m)

            st_data = st_folium(m, width=1200, height=600)

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

