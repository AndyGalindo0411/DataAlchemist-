import streamlit as st  # type: ignore

# === ⚠️ ESTA LÍNEA DEBE IR PRIMERO ===
st.set_page_config(
    page_title="Data Alchemist",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ IMPORTACIÓN DE VISTAS
from inicioFront import vista_inicio
from datos import vista_exploracion
from prediccionFront import vista_prediccion
from introduccion import vista_introduccion
from conclusion import vista_conclusion  # ✅ NUEVA VISTA

# === ESTADO DE NAVEGACIÓN INICIAL ===
if "seccion_activa" not in st.session_state:
    st.session_state.seccion_activa = "Inicio"

# === ESTILO PERSONALIZADO PARA DANU SHOP ===
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

# === BARRA LATERAL (SOLO SI NO ESTÁS EN INTRODUCCIÓN) ===
if st.session_state.seccion_activa != "Inicio":
    with st.sidebar:
        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([25, 100, 25])
        with col2:
            st.image("Imagenes/DanuAnalitica.png", width=120)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # === Cargar estilos si hay
        try:
            with open("style.css", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            pass

        # === CAMBIO DE COLOR DEL SIDEBAR ===
        st.markdown("""
            <style>
            section[data-testid="stSidebar"] {
                background-color: #eef4f7;  /* 🔵 Cambia este color según lo desees */
            }
            </style>
        """, unsafe_allow_html=True)

        # === MENÚ SOLO SI NO ESTÁS EN INTRODUCCIÓN
        st.markdown("### MENÚ")
        if st.button("Inicio"):
            st.session_state.seccion_activa = "Inicio"
        if st.button("Danu Shop"):
            st.session_state.seccion_activa = "Danu Shop"
        if st.button("Exploración de Datos"):
            st.session_state.seccion_activa = "Exploración de Datos"
        if st.button("Conclusión"):
            st.session_state.seccion_activa = "Conclusión"

        st.markdown("<div style='flex-grow: 1; height: 40px;'></div>", unsafe_allow_html=True)

# === RENDERIZADOR PRINCIPAL ===
if st.session_state.seccion_activa == "Inicio":
    vista_introduccion()  # ❌ SIN MENÚ
elif st.session_state.seccion_activa == "Danu Shop":
    vista_inicio()
elif st.session_state.seccion_activa == "Exploración de Datos":
    vista_exploracion()
elif st.session_state.seccion_activa == "Predicción":
    vista_prediccion()
elif st.session_state.seccion_activa == "Conclusión":
    vista_conclusion()
