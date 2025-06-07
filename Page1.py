import streamlit as st  # type: ignore

# ✅ IMPORTACIÓN CORRECTA DEL FRONTEND
from inicioFront import vista_inicio
from datos import vista_exploracion
from prediccionFront import vista_prediccion
from configuracion import vista_configuracion
from introduccion import vista_introduccion

# === Configuración general ===
st.set_page_config(
    page_title="Data Alchemist",
    layout="wide",
    initial_sidebar_state="expanded"  # Por defecto, sidebar abierto
)

# === Estado de navegación ===
if "seccion_activa" not in st.session_state:
    st.session_state.seccion_activa = "Inicio"

# === Si estamos en Danu Shop, colapsar solo visualmente el sidebar al cargar ===
if st.session_state.seccion_activa == "Danu Shop":
    st.markdown("""
        <style>
        [data-testid="collapsedControl"] {
            display: block !important;
        }
        .block-container {
            padding-bottom: 0rem !important;
        }
        html, body, [data-testid="stAppViewContainer"] {
            overflow-y: hidden !important;
        }
        </style>
    """, unsafe_allow_html=True)

# === Sidebar (SIEMPRE presente, pero puede estar colapsado) ===
with st.sidebar:
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([25, 100, 25])
    with col2:
        st.image("Imagenes/DanuAnalitica.png", width=120)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Estilos
    try:
        with open("style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # No rompe si el archivo no está

    st.markdown("### MENÚ")
    if st.button("Inicio"):
        st.session_state.seccion_activa = "Inicio"
    if st.button("Danu Shop"):
        st.session_state.seccion_activa = "Danu Shop"
    if st.button("Exploración de Datos"):
        st.session_state.seccion_activa = "Exploración de Datos"
    
    # ❌ Botón de "Predicción" eliminado
    # if st.button("Predicción"):
    #     st.session_state.seccion_activa = "Predicción"
    
    if st.button("Configuración"):
        st.session_state.seccion_activa = "Configuración"

    st.markdown("<div style='flex-grow: 1; height: 40px;'></div>", unsafe_allow_html=True)

# === Renderizar vista activa ===
if st.session_state.seccion_activa == "Inicio":
    vista_introduccion()
elif st.session_state.seccion_activa == "Danu Shop":
    vista_inicio()
elif st.session_state.seccion_activa == "Exploración de Datos":
    vista_exploracion()
elif st.session_state.seccion_activa == "Predicción":
    vista_prediccion()
elif st.session_state.seccion_activa == "Configuración":
    vista_configuracion()
