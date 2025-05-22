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

# Asegúrate de que st.secrets["USUARIO"] y st.secrets["CONTRASENA"] estén configurados en tu entorno Streamlit Cloud
# Por ejemplo, en .streamlit/secrets.toml:
# USUARIO = "tu_usuario"
# CONTRASENA = "tu_contrasena"
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
        # Asegúrate de tener las imágenes 'Mapa1.png' y 'GEOVISOR.png' en la misma carpeta que tu script
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

    st.stop()

# --- Función para descargar y cargar archivos ZIP de shapefiles ---
@st.cache_data
def descargar_y_cargar_zip(url):
    try:
        r = requests.get(url)
        r.raise_for_status() # Lanza una excepción para errores HTTP
        with zipfile.ZipFile(BytesIO(r.content)) as zip_ref:
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_ref.extractall(tmpdir)
                shp_path = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".shp")]
                if not shp_path:
                    st.error("❌ No se encontró ningún archivo .shp en el ZIP descargado.")
                    return None
                
                gdf = None
                try:
                    gdf = gpd.read_file(shp_path[0])
                except Exception as e:
                    st.warning(f"Advertencia: Error al cargar shapefile con encoding predeterminado. Intentando con 'latin1'. Error: {e}")
                    gdf = gpd.read_file(shp_path[0], encoding='latin1')
                
                # Asegurarse de que el GeoDataFrame esté en CRS 4326 para Folium
                if gdf is not None and gdf.crs != "EPSG:4326":
                    gdf = gdf.to_crs(epsg=4326)
                return gdf

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error al descargar el archivo ZIP: {e}")
        return None
    except zipfile.BadZipFile:
        st.error("❌ El archivo descargado no es un ZIP válido.")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado al cargar el archivo ZIP: {e}")
        return None

def onedrive_a_directo(url_onedrive):
    if "1drv.ms" in url_onedrive:
        r = requests.get(url_onedrive, allow_redirects=True)
        return r.url.replace("redir?", "download?").replace("redir=", "download=")
    return url_onedrive

# Carga el shapefile principal
url_zip = onedrive_a_directo(st.secrets["URL_ZIP"])
gdf_total = descargar_y_cargar_zip(url_zip)

# --- Carga la nueva capa de Resguardos y Consejos (ANT) ---
url_formalizado_zip = "https://raw.githubusercontent.com/lmiguerrero/Ancestrario/main/Formalizado.zip"
gdf_formalizado = descargar_y_cargar_zip(url_formalizado_zip)


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

    # --- Opción para mostrar/ocultar relleno de polígonos ---
    st.sidebar.header("🎨 Estilos del Mapa")
    mostrar_relleno = st.sidebar.checkbox("Mostrar relleno de polígonos", value=True)

    # --- NUEVO: Opción para mostrar/ocultar capa formalizado ---
    st.sidebar.header("🗺️ Capas Base Adicionales")
    mostrar_capa_formalizado = st.sidebar.checkbox("Mostrar Resguardos y Consejos (ANT)", value=False)


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

            # Función de estilo para la capa principal
            def style_function_by_tipo(feature):
                tipo = feature["properties"]["cn_ci"]
                color_borde = "#228B22" if tipo == "ci" else "#8B4513"
                color_relleno = "#228B22" if tipo == "ci" else "#8B4513"
                opacidad_relleno = 0.6 if mostrar_relleno else 0 # Controla la opacidad del relleno
                return {"fillColor": color_relleno, "color": color_borde, "weight": 1, "fillOpacity": opacidad_relleno}

            # Añadir la capa principal filtrada
            folium.GeoJson(
                gdf_filtrado,
                name="Territorios Filtrados", # Nombre para el LayerControl
                style_function=style_function_by_tipo,
                tooltip=folium.GeoJsonTooltip(
                    fields=["id_rtdaf", "nom_terr", "etnia", "departamen", "municipio", "etapa", "estado_act", "tipologia", "area_formateada"],
                    aliases=["ID:", "Territorio:", "Etnia:", "Departamento:", "Municipio:", "Etapa:", "Estado:", "Tipología:", "Área:"],
                    localize=True
                )
            ).add_to(m)

            # --- NUEVO: Añadir la capa de Formalizado si está seleccionada ---
            if mostrar_capa_formalizado and gdf_formalizado is not None:
                def style_formalizado_layer(feature):
                    return {
                        "fillColor": "#A0D8B3",  # Verde claro sutil
                        "color": "#3CB371",     # Borde verde medio
                        "weight": 1,
                        "fillOpacity": 0.4
                    }
                
                # Determinar campos para el tooltip de la capa formalizado dinámicamente
                formalizado_tooltip_fields = []
                formalizado_tooltip_aliases = []
                # Priorizar campos conocidos, si existen
                if 'nom_terr' in gdf_formalizado.columns:
                    formalizado_tooltip_fields.append("nom_terr")
                    formalizado_tooltip_aliases.append("Territorio:")
                if 'etnia' in gdf_formalizado.columns:
                    formalizado_tooltip_fields.append("etnia")
                    formalizado_tooltip_aliases.append("Etnia:")
                if 'departamen' in gdf_formalizado.columns:
                    formalizado_tooltip_fields.append("departamen")
                    formalizado_tooltip_aliases.append("Departamento:")
                
                # Si no se encontraron campos específicos, usar los primeros 3 campos no geométricos
                if not formalizado_tooltip_fields:
                    non_geom_cols = [col for col in gdf_formalizado.columns if col != gdf_formalizado.geometry.name]
                    formalizado_tooltip_fields = non_geom_cols[:3]
                    formalizado_tooltip_aliases = [f"{f.replace('_', ' ').title()}:" for f in formalizado_tooltip_fields]

                folium.GeoJson(
                    gdf_formalizado,
                    name="Resguardos y Consejos (ANT)", # Nombre para el LayerControl
                    style_function=style_formalizado_layer,
                    tooltip=folium.GeoJsonTooltip(
                        fields=formalizado_tooltip_fields,
                        aliases=formalizado_tooltip_aliases,
                        localize=True
                    )
                ).add_to(m)
            
            # Añadir control de capas para alternar visibilidad de las capas GeoJson
            folium.LayerControl().add_to(m)

            # Leyenda HTML
            leyenda_html = '''
            <div style="position: absolute; top: 10px; left: 10px; z-index: 9999;
                         background-color: white; padding: 10px; border: 1px solid #ccc;
                         font-size: 14px; box-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
                <strong>Leyenda</strong><br>
                🟢 Territorio indígena (ci)<br>
                🟤 Territorio afrodescendiente (cn)
            '''
            if mostrar_capa_formalizado:
                leyenda_html += '<br><span style="color:#3CB371;">&#9632;</span> Resguardos/Consejos (ANT)' # Símbolo cuadrado para la capa formalizado
            leyenda_html += '</div>'

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
                    label="🌐 Descargar mapa HTML",
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
