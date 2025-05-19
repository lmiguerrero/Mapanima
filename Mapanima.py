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
    st.markdown("""
        <style>
        .contenedor-login {
            display: flex;
            flex-direction: row;
            height: 100vh;
            width: 100%;
            background-color: #f2f2f2;
        }
        .login-formulario {
            flex: 1;
            padding: 3em;
            background-color: #fefefe;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .login-bienvenida {
            flex: 1;
            background: url('https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Esp%C3%ADritu_del_Agua.jpg/640px-Esp%C3%ADritu_del_Agua.jpg') no-repeat center center;
            background-size: cover;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2em;
        }
        .login-bienvenida-texto {
            background-color: rgba(255,255,255,0.85);
            padding: 2em;
            border-radius: 10px;
            max-width: 400px;
            text-align: justify;
            font-size: 16px;
        }
        </style>
        <div class="contenedor-login">
            <div class="login-formulario">
    """, unsafe_allow_html=True)

    st.sidebar.header("🔐 Acceso restringido")
    usuario = st.sidebar.text_input("Usuario")
    contrasena = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        if usuario.strip().upper() == usuario_valido.strip().upper() and contrasena.strip() == contrasena_valida.strip():
            st.session_state["autenticado"] = True
        else:
            st.error("Usuario o contraseña incorrectos")

    st.markdown("""
            </div>
            <div class="login-bienvenida">
                <div class="login-bienvenida-texto">
                    <h3>Bienvenido a Mapanima</h3>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
                    Pellentesque imperdiet, nisl nec facilisis facilisis, nulla lorem commodo turpis, at aliquam orci nisl nec justo.</p>
                    <p><strong>Este visor fue desarrollado por la Dirección de Asuntos Étnicos de la URT.</strong></p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

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

# --- Banner superior como imagen ---
with st.container():
    st.image("GEOVISOR.png", use_container_width=True)

# (Aquí continúa el resto del visor, basado en gdf_total como en la versión anterior)
