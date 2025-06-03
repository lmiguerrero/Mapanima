# --- VERSION FINAL 21/05/2025 ---
# --- ULTIMA IMPLEMENTACION - CONTORNOS, BARRAS DE CARGA, MENSAJES DE ERROR Y CREDITOS ---
# --- Miguel Guerrero ---

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
    /* Estilo para el pie de página fijo */
    .fixed-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 10px 0;
        background-color: #1b2e1b; /* Fondo verde oscuro */
        color: #b0c9a8; /* Texto verde claro/gris */
        font-size: 0.8em;
        z-index: 1000; /* Asegura que esté por encima de otros contenidos */
        border-top: 1px solid #346b34; /* Un borde sutil */
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
        # 'Mapa1.png' y 'GEOVISOR.png
        st.image("Mapa1.png", use_container_width=True)  # Si quieres cambiar el banner aquí
        st.markdown(
            """
            <div style='padding-top: 1em; font-size: 16px; color: white; text-align: justify;'>
                <p>
                    Bienvenido al visor <strong>Mapanima</strong>. 
                </p>
                <p>
                    Mapanima nace de la fusión entre “mapa” y “ánima”, evocando no solo la representación gráfica de un territorio, sino su alma, su energía viva. Este nombre es una metáfora del territorio, comprendido no como una extensión vacía delimitada por coordenadas, sino como un espacio sagrado, habitado, sentido y narrado por los pueblos originarios.
                </p>
                <p>
                    Mapanima honra la cosmovisión étnica, donde la tierra tiene memoria, espíritu y dignidad; donde cada río, montaña y sendero guarda historias ancestrales. Así, este visor no solo muestra información geográfica: revela un territorio vivo, que respira y se defiende.
                </p>
                <p style='margin-top: 2em; font-style: italic; color: #b0c9a8;'>
                    Desarrollo del equipo de Geoanálisis Étnico – DAE<br>
                    Unidad de Restitución de Tierras
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.image("GEOVISOR.png", width=160)
    
    # --- Footer para la pantalla de login ---
    st.markdown(
        """
        <div class="fixed-footer">
            Realizado por Ing. Topográfico Luis Miguel Guerrero | © 2025. Contacto: luis.guerrero@urt.gov.co
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# --- Función para descargar y cargar archivos ZIP de shapefiles ---
@st.cache_data
def descargar_y_cargar_zip(url):
    try:
        # Añade un spinner para la carga inicial del ZIP
        with st.spinner("Cargando datos geográficos principales... Esto puede tardar unos segundos."):
            r = requests.get(url)
            r.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
            with zipfile.ZipFile(BytesIO(r.content)) as zip_ref:
                with tempfile.TemporaryDirectory() as tmpdir:
                    zip_ref.extractall(tmpdir)
                    shp_path = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".shp")]
                    if not shp_path:
                        st.error("❌ Error: No se encontró ningún archivo .shp en el ZIP descargado. Asegúrate de que el ZIP contenga un shapefile válido.")
                        return None
                    
                    gdf = None
                    try:
                        gdf = gpd.read_file(shp_path[0])
                    except Exception as e:
                        st.warning(f"⚠️ Advertencia: Error al cargar shapefile con encoding predeterminado. Intentando con 'latin1'. (Detalle: {e})")
                        try:
                            gdf = gpd.read_file(shp_path[0], encoding='latin1')
                        except Exception as e_latin1:
                            st.error(f"❌ Error crítico: No se pudo cargar el shapefile ni con encoding predeterminado ni con 'latin1'. (Detalle: {e_latin1})")
                            return None
                    
                    # Asegurarse de que el GeoDataFrame esté en CRS 4326 para Folium
                    if gdf is not None and gdf.crs != "EPSG:4326":
                        st.info("ℹ️ Reproyectando datos a EPSG:4326 para compatibilidad con el mapa.")
                        gdf = gdf.to_crs(epsg=4326)
                    
                    # Asegurar que 'area_ha' sea numérica y sin NaN para los cálculos
                    if gdf is not None and 'area_ha' in gdf.columns:
                        gdf['area_ha'] = pd.to_numeric(gdf['area_ha'], errors='coerce').fillna(0)

                    # Rellenar valores NaN con una cadena vacía y luego convertir todas las columnas no geométricas a tipo string
                    if gdf is not None:
                        for col in gdf.columns:
                            if col != gdf.geometry.name and col != 'area_ha': # No afectar 'area_ha'
                                gdf[col] = gdf[col].fillna('').astype(str) 

                    return gdf

    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Error HTTP al descargar el archivo ZIP: {e}. Por favor, verifica la URL y tu conexión a internet.")
        return None
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ Error de conexión al descargar el archivo ZIP: {e}. Asegúrate de tener conexión a internet.")
        return None
    except zipfile.BadZipFile:
        st.error("❌ El archivo descargado no es un ZIP válido. Asegúrate de que la URL apunte a un archivo ZIP.")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado al cargar el archivo ZIP: {e}. Por favor, contacta al soporte.")
        return None

def onedrive_a_directo(url_onedrive):
    if "1drv.ms" in url_onedrive:
        try:
            r = requests.get(url_onedrive, allow_redirects=True, timeout=10) # Añadir timeout
            r.raise_for_status()
            return r.url.replace("redir?", "download?").replace("redir=", "download=")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error al convertir URL de OneDrive a directa: {e}. Asegúrate de que la URL sea válida y accesible.")
            return url_onedrive # Retorna la original si falla la conversión
    return url_onedrive

url_zip = onedrive_a_directo(st.secrets["URL_ZIP"])
gdf_total = descargar_y_cargar_zip(url_zip)

# --- Banner superior del visor ya autenticado ---
with st.container():
    st.image("GEOVISOR.png", use_container_width=True)

# --- CONTENIDO DEL VISOR ---
if gdf_total is None:
    st.warning("⚠️ No se pudieron cargar los datos geográficos principales. El visor no puede funcionar sin ellos.")
    st.stop() # Detiene la ejecución si los datos principales no se cargaron

# Continuar solo si gdf_total se cargó correctamente
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

# --- Opción para mostrar/ocultar relleno de polígonos ---
st.sidebar.header("🎨 Estilos del Mapa")
mostrar_relleno = st.sidebar.checkbox("Mostrar relleno de polígonos", value=True)

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
        # Asegurarse de que 'area_ha' sea numérica antes de formatear
        # Esto ya se hace en descargar_y_cargar_zip, pero es una doble verificación
        if 'area_ha' in gdf_filtrado.columns:
            gdf_filtrado['area_ha'] = pd.to_numeric(gdf_filtrado['area_ha'], errors='coerce').fillna(0)

        gdf_filtrado["area_formateada"] = gdf_filtrado["area_ha"].apply(
            lambda ha: f"{int(ha)} ha + {int(round((ha - int(ha)) * 10000)):,} m²"
        )

        gdf_filtrado = gdf_filtrado.to_crs(epsg=4326)
        bounds = gdf_filtrado.total_bounds
        centro_lat = (bounds[1] + bounds[3]) / 2
        centro_lon = (bounds[0] + bounds[2]) / 2
        
        # Añade un spinner mientras se genera el mapa
        with st.spinner("Generando mapa..."):
            m = folium.Map(location=[centro_lat, centro_lon], zoom_start=10, tiles=fondos_disponibles[fondo_seleccionado])

            # Función de estilo para la capa principal
            def style_function_by_tipo(feature):
                tipo = feature["properties"]["cn_ci"]
                color_borde = "#228B22" if tipo == "ci" else "#8B4513"
                color_relleno = "#228B22" if tipo == "ci" else "#8B4513"
                opacidad_relleno = 0.6 if mostrar_relleno else 0 # Controla la opacidad del relleno
                return {"fillColor": color_relleno, "color": color_borde, "weight": 1, "fillOpacity": opacidad_relleno}

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
                🟢 Comunidades Indigenas (ci)<br>
                🟤 Comunidades negras, afrocolombianas, raizales y palenqueras (cn)
            </div>
            '''
            m.get_root().html.add_child(folium.Element(leyenda_html))
            m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
            st_folium(m, width=1200, height=600)
    else:
        st.warning("⚠️ No se encontraron territorios que coincidan con los filtros aplicados. Por favor, ajusta tus selecciones.")

    st.subheader("📋 Resultados filtrados")
    if not gdf_filtrado.empty:
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
                Área Cartográfica: <strong>{hectareas} ha + {metros2:} m²</strong>
            </div>
            ''',
            unsafe_allow_html=True
        )
        with st.expander("📥 Opciones de descarga"):
            # Descargar shapefile filtrado como ZIP
            with tempfile.TemporaryDirectory() as tmpdir:
                shp_path = os.path.join(tmpdir, "territorios.shp")
                gdf_filtrado.to_file(shp_path)
                zip_path = shutil.make_archive(shp_path.replace(".shp", ""), 'zip', tmpdir)
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="📆 Descargar shapefile filtrado (.zip)",
                        data=f,
                        file_name="territorios_filtrados.zip",
                        mime="application/zip"
                    )

            # Descargar mapa como HTML
            html_bytes = m.get_root().render().encode("utf-8")
            st.download_button(
                label="🌐 Descargar mapa",
                data=html_bytes,
                file_name="mapa_filtrado.html",
                mime="text/html"
            )

            # Descargar resultados como CSV
            csv_data = gdf_filtrado.drop(columns=["geometry"]).to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📄 Descargar tabla como CSV",
                data=csv_data,
                file_name="resultados_filtrados.csv",
                mime="text/csv"
            )
    else:
        st.info("No hay datos para mostrar en la tabla o descargar con los filtros actuales.")

# --- Footer global para la pantalla principal del visor ---
st.markdown(
    """
    <div class="fixed-footer">
        Realizado por Ing. Topográfico Luis Miguel Guerrero | © 2025. Contacto: luis.guerrero@urt.gov.co
    </div>
    """,
    unsafe_allow_html=True
)

