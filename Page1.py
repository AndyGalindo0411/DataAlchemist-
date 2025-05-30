import streamlit as st  # type: ignore

from inicio import vista_inicio
from datos import vista_exploracion
from visualizacion import vista_visualizacion
from configuracion import vista_configuracion

# Configuración general
st.set_page_config(page_title="Data Alchemist", layout="wide")

# Estado de navegación
if "seccion_activa" not in st.session_state:
    st.session_state.seccion_activa = "Inicio"

# === Sidebar ===

# Espaciado arriba (mínimo para ajustar imagen)
st.sidebar.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

# Imagen centrada
col1, col2, col3 = st.sidebar.columns([25, 100, 25])
with col2:
    st.image("Imagenes/DanuAnalitica.png", width=120)

# Espaciado entre logo y menú
st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# ✅ Cargar estilos CSS externos
with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Menú de navegación
st.sidebar.markdown("### MENÚ")

if st.sidebar.button("Inicio"):
    st.session_state.seccion_activa = "Inicio"

if st.sidebar.button("Exploración de Datos"):
    st.session_state.seccion_activa = "Exploración de Datos"

if st.sidebar.button("Visualización"):
    st.session_state.seccion_activa = "Visualización"

if st.sidebar.button("Configuración"):
    st.session_state.seccion_activa = "Configuración"

# Espacio al fondo de la sidebar para no empalmar branding con menú
st.sidebar.markdown("<div style='flex-grow: 1; height: 40px;'></div>", unsafe_allow_html=True)

# === Vista activa ===
if st.session_state.seccion_activa == "Inicio":
    vista_inicio()
elif st.session_state.seccion_activa == "Exploración de Datos":
    vista_exploracion()
elif st.session_state.seccion_activa == "Visualización":
    vista_visualizacion()
elif st.session_state.seccion_activa == "Configuración":
    vista_configuracion()
