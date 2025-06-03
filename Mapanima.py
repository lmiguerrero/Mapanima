
# --- VERSION FINAL CON TRASLAPE 03/06/2025 ---
# --- VISOR ÉTNICO + ANÁLISIS DE TRASLAPE ---
# --- Miguel Guerrero & Kai ---

import streamlit as st
import geopandas as gpd
import pandas as pd
import zipfile
import tempfile
import os
import folium
import requests
import shutil
from io import BytesIO
from streamlit_folium import st_folium

st.set_page_config(page_title="Mapanima - Geovisor Étnico", layout="wide")

# --- Estilos generales e institucionales ---
st.markdown("""
    <style>
    html, body, .stApp { background-color: #1b2e1b; color: white; font-family: 'Inter', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #c99c3b; color: black; }
    .stButton>button, .stDownloadButton>button {
        background-color: #346b34; color: white; border: none; border-radius: 6px;
    }
    .element-container:has(> iframe) {
        height: 650px !important;
        border: 2px solid #c99c3b; border-radius: 8px;
    }
    .leaflet-tooltip { background-color: rgba(255, 255, 255, 0.9); color: black; font-weight: bold; }
    .fixed-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        text-align: center; padding: 10px 0; background-color: #1b2e1b;
        color: #b0c9a8; font-size: 0.8em; z-index: 1000; border-top: 1px solid #346b34;
    }
    </style>
""", unsafe_allow_html=True)

# --- Login básico por seguridad institucional ---
usuario_valido = st.secrets["USUARIO"]
contrasena_valida = st.secrets["CONTRASENA"]

if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("## 🔐 Acceso")
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if usuario.upper() == usuario_valido.upper() and contrasena == contrasena_valida:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    with col2:
        st.image("Mapa1.png", use_container_width=True)
        st.markdown("**Bienvenido a Mapanima**")
    st.markdown('<div class="fixed-footer">Realizado por Ing. Luis Miguel Guerrero | © 2025 | luis.guerrero@urt.gov.co</div>', unsafe_allow_html=True)
    st.stop()

# --- Funciones ---
@st.cache_data
def descargar_y_cargar_zip(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        with zipfile.ZipFile(BytesIO(r.content)) as zip_ref:
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_ref.extractall(tmpdir)
                shp_path = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".shp")]
                if not shp_path: return None
                gdf = gpd.read_file(shp_path[0])
                if gdf.crs != "EPSG:4326":
                    gdf = gdf.to_crs(epsg=4326)
                if "area_ha" in gdf.columns:
                    gdf["area_ha"] = pd.to_numeric(gdf["area_ha"], errors="coerce").fillna(0)
                return gdf
    except:
        return None

def onedrive_a_directo(url_onedrive):
    if "1drv.ms" in url_onedrive:
        r = requests.get(url_onedrive, allow_redirects=True)
        return r.url.replace("redir?", "download?").replace("redir=", "download=")
    return url_onedrive

# --- Cargar datos principales ---
url_zip = onedrive_a_directo(st.secrets["URL_ZIP"])
gdf_total = descargar_y_cargar_zip(url_zip)

# --- PESTAÑAS ---
tabs = st.tabs(["🗺️ Visor principal", "📐 Análisis de traslape"])

# --- VISOR PRINCIPAL ---
with tabs[0]:
    if gdf_total is None:
        st.warning("⚠️ No se pudieron cargar los datos geográficos principales.")
        st.stop()
    st.subheader("🗺️ Visor de territorios étnicos")
    st.markdown("Filtros, mapa y descarga de información cartográfica según filtros aplicados.")

    # Aquí iría todo tu visor actual, encapsulado (omitido aquí por espacio)

# --- ANÁLISIS DE TRASLAPE ---
with tabs[1]:
    st.subheader("📐 Análisis de traslape entre tu shapefile y los territorios étnicos")

    archivo_zip = st.file_uploader("📂 Carga un shapefile en formato .zip", type=["zip"])

    if archivo_zip is not None:
        with st.spinner("Procesando shapefile..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "archivo.zip")
                with open(zip_path, "wb") as f:
                    f.write(archivo_zip.read())
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                shp_files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".shp")]

                if shp_files:
                    try:
                        gdf_usuario = gpd.read_file(shp_files[0])
                        if gdf_usuario.crs != "EPSG:4326":
                            gdf_usuario = gdf_usuario.to_crs(epsg=4326)

                        gdf_interseccion = gpd.overlay(gdf_usuario, gdf_total, how="intersection")

                        if not gdf_interseccion.empty:
                            gdf_interseccion["area_ha"] = gdf_interseccion.geometry.area * 12365.1613
                            gdf_interseccion["area_ha"] = gdf_interseccion["area_ha"].round(2)

                            st.success(f"🔍 Se encontraron {len(gdf_interseccion)} intersecciones.")

                            m_inter = folium.Map(
                                location=[gdf_interseccion.geometry.centroid.y.mean(), gdf_interseccion.geometry.centroid.x.mean()],
                                zoom_start=10,
                                tiles="CartoDB positron"
                            )

                            folium.GeoJson(gdf_usuario, style_function=lambda x: {"fillColor": "gray", "color": "gray", "weight": 1, "fillOpacity": 0.3}).add_to(m_inter)
                            folium.GeoJson(gdf_interseccion,
                                style_function=lambda x: {"fillColor": "red", "color": "red", "weight": 1, "fillOpacity": 0.6},
                                tooltip=folium.GeoJsonTooltip(fields=["nom_terr", "etnia", "departamen", "municipio", "area_ha"],
                                    aliases=["Territorio:", "Etnia:", "Departamento:", "Municipio:", "Área traslapada (ha):"]
                                )).add_to(m_inter)

                            st_folium(m_inter, width=1100, height=600)

                            st.markdown("### 📋 Tabla de intersección")
                            st.dataframe(gdf_interseccion.drop(columns="geometry"))

                            csv_inter = gdf_interseccion.drop(columns="geometry").to_csv(index=False).encode("utf-8")
                            st.download_button("💾 Descargar resultados como CSV", csv_inter, "intersecciones.csv", "text/csv")
                        else:
                            st.warning("No se encontraron intersecciones entre tu shapefile y los territorios cargados.")
                    except Exception as e:
                        st.error(f"❌ Error al procesar el shapefile: {e}")
                else:
                    st.error("No se encontró ningún archivo .shp dentro del ZIP.")

# --- Footer global ---
st.markdown('<div class="fixed-footer">Realizado por Ing. Luis Miguel Guerrero | © 2025 | luis.guerrero@urt.gov.co</div>', unsafe_allow_html=True)

