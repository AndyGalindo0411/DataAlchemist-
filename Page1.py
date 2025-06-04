import streamlit as st  # type: ignore

# ✅ IMPORTACIÓN CORRECTA DEL FRONTEND
from inicioFront import vista_inicio
from datos import vista_exploracion
from prediccion import vista_prediccion
from configuracion import vista_configuracion


# === Configuración general ===
st.set_page_config(page_title="Data Alchemist", layout="wide")

# === Estado de navegación ===
if "seccion_activa" not in st.session_state:
    st.session_state.seccion_activa = "Inicio"

# === Sidebar ===

# Espaciado arriba
st.sidebar.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

# Imagen centrada
col1, col2, col3 = st.sidebar.columns([25, 100, 25])
with col2:
    st.image("Imagenes/DanuAnalitica.png", width=120)

# Espaciado entre logo y menú
st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Cargar estilos CSS
with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Menú lateral
st.sidebar.markdown("### MENÚ")

if st.sidebar.button("Inicio"):
    st.session_state.seccion_activa = "Inicio"
if st.sidebar.button("Exploración de Datos"):
    st.session_state.seccion_activa = "Exploración de Datos"
if st.sidebar.button("Predicción"):
    st.session_state.seccion_activa = "Predicción"
if st.sidebar.button("Configuración"):
    st.session_state.seccion_activa = "Configuración"

# Espacio inferior en el sidebar
st.sidebar.markdown("<div style='flex-grow: 1; height: 40px;'></div>", unsafe_allow_html=True)

# === Renderizar vista activa ===
if st.session_state.seccion_activa == "Inicio":
    vista_inicio()
elif st.session_state.seccion_activa == "Exploración de Datos":
    vista_exploracion()
elif st.session_state.seccion_activa == "Predicción":
    vista_prediccion()
elif st.session_state.seccion_activa == "Configuración":
    vista_configuracion()
