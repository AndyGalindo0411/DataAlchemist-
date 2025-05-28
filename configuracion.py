# configuracion.py
import streamlit as st # type: ignore

def vista_configuracion():
    st.header("Configuración de la Aplicación")

    st.subheader("Preferencias de Usuario")
    tema = st.selectbox("Tema de visualización:", ["Claro", "Oscuro"])
    mostrar_logo = st.checkbox("Mostrar logotipo en pantalla principal", value=True)
    nombre_usuario = st.text_input("Nombre del usuario", value="Invitado")

    st.markdown("---")
    st.subheader("Parámetros Avanzados")
    refresh_rate = st.slider("Frecuencia de actualización de datos (segundos)", 5, 60, 15)

    st.markdown("---")
    st.success(f"Configuración aplicada para: **{nombre_usuario}** con tema **{tema}** y actualización cada {refresh_rate} segundos.")
