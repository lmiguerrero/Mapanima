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

# --- Autenticación segura usando secrets ---
usuario_valido = st.secrets["USUARIO"]
contrasena_valida = st.secrets["CONTRASENA"]

def login():
    st.sidebar.header("🔐 Acceso restringido")
    usuario = st.sidebar.text_input("Usuario")
    contrasena = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        if usuario == usuario_valido and contrasena == contrasena_valida:
            st.session_state["autenticado"] = True
        else:
            st.error("Usuario o contraseña incorrectos")

if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
    login()
    st.stop()

# --- Descargar y cargar automáticamente el ZIP desde secrets ---
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

# 🔄 IMPORTANTE: convertir URL de OneDrive a enlace directo de descarga
def onedrive_a_directo(url_onedrive):
    if "1drv.ms" in url_onedrive:
        r = requests.get(url_onedrive, allow_redirects=True)
        return r.url.replace("redir?", "download?").replace("redir=", "download=")
    return url_onedrive

url_zip = onedrive_a_directo(st.secrets["URL_ZIP"])
gdf_total = descargar_y_cargar_zip(url_zip)

# --- Estilo visual: tipografía, fondo, banner, leyenda ---

st.markdown("""
    <style>
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
    .stMarkdown, .stExpander {
        color: white;
    }
    .element-container:has(> iframe) {
        height: 650px !important;
        margin-bottom: 0rem !important;
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

# (El resto del visor debe continuar aquí con la lógica basada en gdf_total ya cargado)
