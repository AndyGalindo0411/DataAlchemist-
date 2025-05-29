import streamlit as st

# Importar vistas
from inicio import vista_inicio
from datos import vista_exploracion
from visualizacion import vista_visualizacion
from configuracion import vista_configuracion

# Configuración de página
st.set_page_config(page_title="Mi App Completa", layout="wide")

# Inicializar estado
if "seccion_activa" not in st.session_state:
    st.session_state.seccion_activa = "Inicio"

# --- Estilo uniforme para botones ---
button_css = """
<style>
div.stButton > button {
    width: 100%;
    margin-bottom: 10px;
    height: 45px;
    font-size: 16px;
}
</style>
"""
st.sidebar.markdown(button_css, unsafe_allow_html=True)

# Sidebar con botones uniformes
st.sidebar.title("Panel de control")

if st.sidebar.button("Inicio"):
    st.session_state.seccion_activa = "Inicio"

if st.sidebar.button("Exploración de Datos"):
    st.session_state.seccion_activa = "Exploración de Datos"

if st.sidebar.button("Visualización"):
    st.session_state.seccion_activa = "Visualización"

if st.sidebar.button("Configuración"):
    st.session_state.seccion_activa = "Configuración"

st.sidebar.markdown("---")
st.sidebar.write("Data Alchemist v1.0")

# Enrutamiento según la vista activa
if st.session_state.seccion_activa == "Inicio":
    vista_inicio()
elif st.session_state.seccion_activa == "Exploración de Datos":
    vista_exploracion()
elif st.session_state.seccion_activa == "Visualización":
    vista_visualizacion()
elif st.session_state.seccion_activa == "Configuración":
    vista_configuracion()
