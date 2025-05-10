# 🗺️ Mapanima - Geovisor Étnico

**Mapanima** es una herramienta interactiva desarrollada en Python con Streamlit para visualizar, consultar y exportar información geográfica de territorios indígenas y afrodescendientes en Colombia. Su nombre proviene de la combinación de las palabras _Mapa_ + _Ánima_, evocando la idea de un mapa con alma, un visor que respeta la identidad y la vida de los territorios étnicos.

---

## 🚀 ¿Qué permite hacer?

- Cargar un archivo `.zip` con un shapefile unificado de territorios étnicos (CI y CN).
- Aplicar filtros por:
  - Etapa del proceso (Administrativa, Judicial, Posfallo)
  - Estado del caso (según clasificación DAE)
  - Tipo de territorio (`ci` o `cn`)
  - Departamento
  - ID (RTDAF)
  - Nombre de territorio
- Visualizar los territorios filtrados sobre un mapa base
- Descargar el mapa como archivo HTML interactivo
- Ver una tabla con los resultados filtrados
- Descargar los resultados como archivo CSV

---

## 🧰 Tecnologías utilizadas

- [Streamlit](https://streamlit.io)
- [GeoPandas](https://geopandas.org)
- [Folium](https://python-visualization.github.io/folium/)
- [streamlit-folium](https://github.com/randyzwitch/streamlit-folium)
- Pandas

---

## 📦 Requisitos para ejecutarlo localmente

1. Clona este repositorio:

```bash
git clone https://github.com/lmguerrerov/Mapanima.git
cd Mapanima
