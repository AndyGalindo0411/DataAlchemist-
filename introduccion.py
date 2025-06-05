import streamlit as st

def vista_introduccion():
    st.markdown("<h1>Introducción a Data Alchemist</h1>", unsafe_allow_html=True)
    st.write("Navega entre las secciones utilizando los botones.")

    # Estado persistente del índice del carrusel
    if "slide_index" not in st.session_state:
        st.session_state.slide_index = 1

    slide = st.session_state.slide_index

    # Mostrar contenido del slide actual
    if slide == 1:
        st.subheader("¿Qué es Data Alchemist?")
        st.write(
            st.image("imagenes/1.png")
        )

    elif slide == 2:
        st.subheader("¿Qué puedo hacer?")
        st.write(
            st.image("imagenes/2.png")

        )

    elif slide == 3:
        st.subheader("¿Qué incluye la parte de predicción?")
        st.write(
            st.image("imagenes/3.png")

        )

    elif slide == 4:
        st.subheader("¿Cómo empezar?")
        st.write(
            st.image("imagenes/4.png")

        )

    elif slide == 5:
        st.subheader("Quinta sección")
        st.write(
            st.image("imagenes/5.png")

        )

    # --- Navegación con flechas (condicional) ---
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if slide > 1:
            if st.button("Anterior"):
                st.session_state.slide_index -= 1
    with col3:
        if slide < 5:
            if st.button("Siguiente"):
                st.session_state.slide_index += 1

    # --- Indicador visual tipo carrusel (ajustado a 5 slides) ---
    st.markdown(
        f"<div style='text-align:center; font-size: 22px; margin-top: 10px'>{' '.join(['●' if i == slide else '○' for i in range(1, 6)])}</div>",
        unsafe_allow_html=True
    )

    st.markdown("<hr style='border-top: 1px solid #bbb;'>", unsafe_allow_html=True)
