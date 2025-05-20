#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import geopandas as gpd
import pandas as pd
import zipfile
import tempfile
import os
import folium
import requests
from io import BytesIO
from streamlit_folium import st_folium

st.set_page_config(page_title="Mapanima - Geovisor Étnico", layout="wide")

# --- Estilos generales e institucionales ---
st.markdown("""
    <style>
    .login-left {
        background-color: #c99c3b;
        padding: 3em;
        height: 100vh;
        color: black;
    }
    .login-right {
        background-color: #1b2e1b;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    .login-right img {
        max-width: 100%;
        max-height: 90%;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(255,255,255,0.3);
    }
    html, body, .stApp {
        background-color: #1b2e1b;
        color: white;
        font-family: 'Inter', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #c99c3b;
        color: black;
    }
    .stButton>button {
        background-color: #346b34;
        color: white;
        border: none;
        border-radius: 6px;
    }
    .stTextInput>div>div>input,
    .stSelectbox>div>div>div>input {
        color: black;
        background-color: white;
        border-radius: 4px;
    }
    .element-container:has(> iframe) {
        height: 650px !important;
        border: 2px solid #c99c3b;
        border-radius: 8px;
    }
    .leaflet-tooltip {
        background-color: rgba(255, 255, 255, 0.9);
        color: black;
        font-weight: bold;
    }
    .stDataFrame {
        background-color: white;
        color: black;
        border-radius: 8px;
    }
    .stDownloadButton > button {
        background-color: #ffffff;
        color: #1b2e1b;
        border: 1px solid #346b34;
        border-radius: 6px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Personalización de estilos ---
st.markdown("""
    <style>
    label {
        color: white !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Login con columnas ---

usuario_valido = st.secrets["USUARIO"]
contrasena_valida = st.secrets["CONTRASENA"]

if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown("<h2>🔐 Acceso restringido</h2>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if usuario.strip().upper() == usuario_valido.strip().upper() and contrasena.strip() == contrasena_valida.strip():
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    with col2:
        st.image("GEOVISOR.png", use_container_width=True)
        st.markdown("""
            <div style='padding-top: 1em; font-size: 16px; color: white; text-align: justify;'>
                Bienvenido al visor <strong>Mapanima</strong>. Esta plataforma permite consultar y visualizar los territorios étnicos
                reconstruidos por el equipo de la Dirección de Asuntos Étnicos de la URT, brindando herramientas técnicas para el análisis espacial de los procesos.
            </div>
        """, unsafe_allow_html=True)

    st.stop()

# --- Carga ZIP remoto desde OneDrive ---
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

def onedrive_a_directo(url_onedrive):
    if "1drv.ms" in url_onedrive:
        r = requests.get(url_onedrive, allow_redirects=True)
        return r.url.replace("redir?", "download?").replace("redir=", "download=")
    return url_onedrive

url_zip = onedrive_a_directo(st.secrets["URL_ZIP"])
gdf_total = descargar_y_cargar_zip(url_zip)

# --- Banner superior del visor ya autenticado ---
with st.container():
    st.image("GEOVISOR.png", use_container_width=True)

# --- CONTENIDO DEL VISOR ---
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

    fondos_disponibles = {
        "OpenStreetMap": "OpenStreetMap",
        "CartoDB Claro (Positron)": "CartoDB positron",
        "CartoDB Oscuro": "CartoDB dark_matter",
        "Satélite (Esri)": "Esri.WorldImagery",
        "Esri NatGeo World Map": "Esri.NatGeoWorldMap",
        "Esri World Topo Map": "Esri.WorldTopoMap"
    }
    fondo_seleccionado = st.sidebar.selectbox("🗺️ Fondo del mapa", list(fondos_disponibles.keys()), index=1)

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
            gdf_filtrado["area_formateada"] = gdf_filtrado["area_ha"].apply(
                lambda ha: f"{int(ha)} ha + {int(round((ha - int(ha)) * 10000)):,} m²"
            )

            gdf_filtrado = gdf_filtrado.to_crs(epsg=4326)
            bounds = gdf_filtrado.total_bounds
            centro_lat = (bounds[1] + bounds[3]) / 2
            centro_lon = (bounds[0] + bounds[2]) / 2
            m = folium.Map(location=[centro_lat, centro_lon], zoom_start=10, tiles=fondos_disponibles[fondo_seleccionado])

            def style_function_by_tipo(feature):
                tipo = feature["properties"]["cn_ci"]
                color = "#228B22" if tipo == "ci" else "#8B4513"
                return {"fillColor": color, "color": color, "weight": 1, "fillOpacity": 0.6}

            folium.GeoJson(
                gdf_filtrado,
                style_function=style_function_by_tipo,
                tooltip=folium.GeoJsonTooltip(
                    fields=["id_rtdaf", "nom_terr", "etnia", "departamen", "municipio", "etapa", "estado_act", "tipologia", "area_formateada"],
                    aliases=["ID:", "Territorio:", "Etnia:", "Departamento:", "Municipio:", "Etapa:", "Estado:", "Tipología:", "Área:"],
                    localize=True
                )
            ).add_to(m)

            leyenda_html = '''
            <div style="position: absolute; top: 10px; left: 10px; z-index: 9999;
                        background-color: white; padding: 10px; border: 1px solid #ccc;
                        font-size: 14px; box-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
                <strong>Leyenda</strong><br>
                🟢 Territorio indígena (ci)<br>
                🟤 Territorio afrodescendiente (cn)
            </div>
            '''
            m.get_root().html.add_child(folium.Element(leyenda_html))
            m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
            st_folium(m, width=1200, height=600)

            st.subheader("📋 Resultados filtrados")
            st.dataframe(gdf_filtrado.drop(columns=["geometry", "area_formateada"]))

            # Estadísticas
            total_territorios = len(gdf_filtrado)
            area_total = gdf_filtrado["area_ha"].sum()
            hectareas = int(area_total)
            metros2 = int(round((area_total - hectareas) * 10000))
            cuenta_ci = (gdf_filtrado["cn_ci"] == "ci").sum()
            cuenta_cn = (gdf_filtrado["cn_ci"] == "cn").sum()

            st.markdown(
                f'''
                <div style='
                    margin-top: 1em;
                    margin-bottom: 1.5em;
                    padding: 0.7em;
                    background-color: #e8f5e9;
                    border-radius: 8px;
                    font-size: 16px;
                    color: #2e7d32;'>
                    <strong>📊 Estadísticas del resultado:</strong><br>
                    Territorios filtrados: <strong>{total_territorios}</strong><br>
                    ▸ Comunidades indígenas (ci): <strong>{cuenta_ci}</strong><br>
                    ▸ Consejos comunitarios (cn): <strong>{cuenta_cn}</strong><br>
                    Área total: <strong>{hectareas} ha + {metros2:,} m²</strong>
                </div>
                ''',
                unsafe_allow_html=True
            )
