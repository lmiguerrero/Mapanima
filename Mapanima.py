#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
st.set_page_config(page_title="Mapanima - Geovisor Étnico", layout="wide")

# --- Página de bienvenida con login directo ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("""
    <style>
    .stApp {
        background-color: #1b2e1b;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    .seccion {
        padding: 2em;
        text-align: center;
    }
    .texto-bienvenida {
        font-size: 18px;
        text-align: justify;
        max-width: 900px;
        margin: auto;
    }
    .fotos-container {
        display: flex;
        justify-content: center;
        gap: 1em;
        margin-top: 1em;
    }
    .fotos-container img {
        width: 28%;
        border-radius: 12px;
        box-shadow: 0 0 8px rgba(255,255,255,0.2);
    }
    .areas-container {
        display: flex;
        justify-content: center;
        gap: 1em;
        margin-top: 2em;
    }
    .area {
        background-color: #2a4a2a;
        padding: 1em;
        border-radius: 10px;
        width: 28%;
    }
    input[type="text"], input[type="password"] {
        background-color: #e8f5e9 !important;
        color: #1b2e1b !important;
        font-weight: bold;
        border-radius: 8px;
        height: 45px;
        font-size: 16px;
    }
    label {
        color: #c99c3b !important;
        font-weight: bold;
    }
    button[kind="primary"] {
        background-color: #c99c3b !important;
        color: #1b2e1b !important;
        font-weight: bold;
        border-radius: 8px;
        height: 45px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌿 Mapanima")
    st.image("GEOVISOR.png", use_container_width=True)

    st.markdown("""
    <div class='seccion texto-bienvenida'>
        <p><strong>Mapanima</strong> es un visor étnico desarrollado para la Unidad de Restitución de Tierras, que representa el alma y la memoria territorial de los pueblos indígenas y comunidades negras de Colombia.</p>
        <p>Su propósito es facilitar el análisis espacial de los procesos de restitución con una plataforma ligera, interactiva y respetuosa del carácter sagrado de la tierra.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='fotos-container'>
        <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Amazonas_rainforest.jpg/640px-Amazonas_rainforest.jpg'>
        <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Territorio_indigena_Nasa.jpg/640px-Territorio_indigena_Nasa.jpg'>
        <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Community_mapping_workshop.jpg/640px-Community_mapping_workshop.jpg'>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='areas-container'>
        <div class='area'><h4>Territorio</h4><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur id fermentum justo.</p></div>
        <div class='area'><h4>Memoria</h4><p>Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia.</p></div>
        <div class='area'><h4>Cosmovisión</h4><p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque.</p></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("🌍 Ingresar al visor")

        if submit:
            if usuario == st.secrets["USUARIO"] and contrasena == st.secrets["CONTRASENA"]:
                st.session_state["autenticado"] = True
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.stop()

#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
st.set_page_config(page_title="Mapanima - Geovisor Étnico", layout="wide")

# --- Estilo visual: tipografía, fondo, banner, leyenda ---

st.markdown("""
    <style>
    /* Fondo general verde oscuro */
    html, body, .stApp {
        background-color: #1b2e1b;
        color: white;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar con color institucional (café) */
    section[data-testid="stSidebar"] {
        background-color: #c99c3b;
        color: black;
    }

    /* Botones en verde más claro */
    .stButton>button {
        background-color: #346b34;
        color: white;
        border: none;
        border-radius: 6px;
    }

    /* Mejor contraste en inputs */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>div>input {
        color: black;
        background-color: white;
        border-radius: 4px;
    }

    /* Expanders, títulos y cajas de markdown */
    .stMarkdown, .stExpander {
        color: white;
    }

    /* Estilo del mapa (fondo claro dentro del iframe) */
    .element-container:has(> iframe) {
        height: 650px !important;
        margin-bottom: 0rem !important;
        border: 2px solid #c99c3b;
        border-radius: 8px;
    }

    /* Tooltip del mapa */
    .leaflet-tooltip {
        background-color: rgba(255, 255, 255, 0.9);
        color: black;
        font-weight: bold;
    }

    /* Tabla de resultados */
    .stDataFrame {
        background-color: white;
        color: black;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)


import geopandas as gpd
import pandas as pd
import zipfile
import tempfile
import os
import folium
from streamlit_folium import st_folium

# --- Banner superior como imagen ---
with st.container():
    st.markdown("<div class='banner'>", unsafe_allow_html=True)
    st.image("GEOVISOR.png", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Título e introducción ---
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

# --- Cargar ZIP con shapefile ---
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

# --- Subir archivo ---

import requests
from io import BytesIO

# --- Convertir link corto de OneDrive a link de descarga directa ---
def onedrive_a_directo(url_onedrive):
    if "1drv.ms" in url_onedrive:
        r = requests.get(url_onedrive, allow_redirects=True)
        return r.url.replace("redir?", "download?").replace("redir=", "download=")
    return url_onedrive

# --- Descargar y cargar automáticamente el ZIP desde la URL transformada ---
@st.cache_data
def descargar_y_cargar_zip(url):
    r = requests.get(url)
    if r.status_code != 200:
        st.error("❌ No se pudo descargar el archivo ZIP.")
        return None
    with zipfile.ZipFile(BytesIO(r.content)) as zip_ref:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_ref.extractall(tmpdir)
            shp_path = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".shp")]
            if not shp_path:
                st.error("❌ No se encontró ningún archivo .shp en el ZIP descargado.")
                return None
            return gpd.read_file(shp_path[0])

# --- Ejecutar descarga automática desde secrets
url_zip = onedrive_a_directo(st.secrets["URL_ZIP"])
gdf_total = descargar_y_cargar_zip(url_zip)

if gdf_total is not None:
    st.success("✅ Capa cargada automáticamente desde fuente protegida.")

# --- Si hay datos cargados ---
if gdf_total is not None:
    gdf_total['etapa'] = gdf_total['etapa'].str.lower()
    gdf_total['estado_act'] = gdf_total['estado_act'].str.strip()
    gdf_total['cn_ci'] = gdf_total['cn_ci'].str.lower()

    st.sidebar.header("🎯 Filtros")
    etapa_sel = st.sidebar.multiselect("Filtrar por etapa", sorted(gdf_total['etapa'].dropna().unique()))
    estado_sel = st.sidebar.multiselect("Filtrar por estado del caso", sorted(gdf_total['estado_act'].dropna().unique()))
    tipo_sel = st.sidebar.multiselect("Filtrar por tipo de territorio", sorted(gdf_total['cn_ci'].dropna().unique()))
    depto_sel = st.sidebar.multiselect("Filtrar por departamento", sorted(gdf_total['departamen'].dropna().unique()))
    nombre_opciones = sorted(gdf_total['nom_terr'].dropna().unique())
    nombre_seleccionado = st.sidebar.selectbox("🔍 Buscar por nombre (nom_terr)", options=[""] + nombre_opciones)
    id_buscar = st.sidebar.text_input("🔍 Buscar por ID (id_rtdaf)")

    st.sidebar.header("⚙️ Rendimiento")
    usar_simplify = st.sidebar.checkbox("Simplificar geometría", value=True)
    tolerancia = st.sidebar.slider("Nivel de simplificación", 0.00001, 0.001, 0.0001, step=0.00001, format="%.5f")

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
        if nombre_seleccionado:
            gdf_filtrado = gdf_filtrado[gdf_filtrado["nom_terr"] == nombre_seleccionado]
        if usar_simplify:
            gdf_filtrado["geometry"] = gdf_filtrado["geometry"].simplify(tolerancia, preserve_topology=True)

        st.subheader("🗺️ Mapa filtrado")

        if not gdf_filtrado.empty:
            # Calcular área formateada
            gdf_filtrado["area_formateada"] = gdf_filtrado["area_ha"].apply(
                lambda ha: f"{int(ha)} ha + {int(round((ha - int(ha)) * 10000)):,} m²"
            )

            gdf_filtrado = gdf_filtrado.to_crs(epsg=4326)
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

            folium.GeoJson(
                gdf_filtrado,
                style_function=style_function_by_tipo,
                tooltip=folium.GeoJsonTooltip(
                    fields=["id_rtdaf", "nom_terr", "etnia", "departamen", "municipio", "etapa", "estado_act", "area_formateada"],
                    aliases=["ID:", "Territorio:", "Etnia:", "Departamento:", "Municipio:", "Etapa:", "Estado:", "Área:"],
                    localize=True
                )
            ).add_to(m)

            leyenda_html = """
            <div style='position: absolute; top: 10px; left: 10px; z-index: 9999;
                        background-color: white; padding: 10px; border: 1px solid #ccc;
                        font-size: 14px; box-shadow: 2px 2px 4px rgba(0,0,0,0.1);'>
                <strong>Leyenda</strong><br>
                🟢 Territorio indígena (ci)<br>
                🟤 Territorio afrodescendiente (cn)
            </div>
            """
            m.get_root().html.add_child(folium.Element(leyenda_html))
            m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
            st_data = st_folium(m, width=1200, height=600)

            st.subheader("📋 Resultados filtrados")
            st.dataframe(gdf_filtrado.drop(columns=["geometry", "area_formateada"]))

            # Descargar CSV
            csv = gdf_filtrado.drop(columns="geometry").to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Descargar CSV de resultados", data=csv, file_name="resultados_filtrados.csv", mime="text/csv")

            # Descargar SHP como ZIP
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "shapefile_filtrado.zip")
                shp_base = os.path.join(tmpdir, "shapefile_filtrado")
                gdf_filtrado.drop(columns="area_formateada").to_file(shp_base + ".shp", driver="ESRI Shapefile", encoding="utf-8")
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
                        fpath = shp_base + ext
                        if os.path.exists(fpath):
                            zipf.write(fpath, arcname="shapefile_filtrado" + ext)
                with open(zip_path, "rb") as f:
                    st.download_button("⬇️ Descargar Shapefile filtrado (.zip)", data=f, file_name="shapefile_filtrado.zip", mime="application/zip")

            # Descargar HTML
            if st.sidebar.button("💾 Exportar mapa a HTML"):
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmpfile:
                    m.save(tmpfile.name)
                    st.success("✅ Mapa exportado correctamente.")
                    with open(tmpfile.name, "rb") as f:
                        st.download_button("⬇️ Descargar HTML del mapa", data=f, file_name="mapa_etnico_filtrado.html", mime="text/html")

        else:
            st.warning("⚠️ No se encontraron resultados con los filtros aplicados.")

# --- Créditos ---
st.markdown("""---""")
st.markdown(
    "<div style='text-align: center; font-size: 14px;'>"
    "Realizado por <strong>Ing. Luis Miguel Guerrero</strong> — DAE — "
    "<a href='mailto:luis.guerrero@urt.gov.co'>luis.guerrero@urt.gov.co</a>"
    "</div>",
    unsafe_allow_html=True
)
