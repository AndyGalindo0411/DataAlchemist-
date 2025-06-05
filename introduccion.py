import streamlit as st

def vista_introduccion():
    st.markdown("<h1>Introducción a Data Alchemist</h1>", unsafe_allow_html=True)
    st.write("Navega entre las secciones utilizando los botones.")

    if "slide_index" not in st.session_state:
        st.session_state.slide_index = 1

    slide = st.session_state.slide_index

    if slide == 1:
        st.subheader("¿Qué es Data Alchemist?")
        st.image("imagenes/1.png")

    elif slide == 2:
        st.subheader("¿Qué puedo hacer?")
        st.image("imagenes/2.png")

    elif slide == 3:
        st.subheader("¿Qué incluye la parte de predicción?")
        st.image("imagenes/3.png")

    elif slide == 4:
        st.subheader("¿Cómo empezar?")
        st.image("imagenes/4.png")

    elif slide == 5:
        st.subheader("Quinta sección")
        st.image("imagenes/5.png")

    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if slide > 1:
            if st.button("Anterior"):
                st.session_state.slide_index -= 1
    with col3:
        if slide < 5:
            if st.button("Siguiente"):
                st.session_state.slide_index += 1

    st.markdown(
        f"<div style='text-align:center; font-size: 22px; margin-top: 10px'>{' '.join(['●' if i == slide else '○' for i in range(1, 6)])}</div>",
        unsafe_allow_html=True
    )

    st.markdown("<hr style='border-top: 1px solid #bbb;'>", unsafe_allow_html=True)
