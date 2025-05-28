# Page1.py
import streamlit as st

# Importar vistas
from inicio import vista_inicio
from datos import vista_exploracion
from visualizacion import vista_visualizacion
from configuracion import vista_configuracion

# Configuración de página
st.set_page_config(page_title="Mi App Completa", layout="wide")

# Sidebar
st.sidebar.title("Panel de control")
selected_option = st.sidebar.radio(
    "Selecciona una sección",
    ["Inicio", "Exploración de Datos", "Visualización", "Configuración"]
)
st.sidebar.markdown("---")
st.sidebar.write("Data Alchemist v1.0")

# Enrutador
if selected_option == "Inicio":
    vista_inicio()
elif selected_option == "Exploración de Datos":
    vista_exploracion()
elif selected_option == "Visualización":
    vista_visualizacion()
elif selected_option == "Configuración":
    vista_configuracion()
