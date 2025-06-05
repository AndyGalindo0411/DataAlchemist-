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
            "Es una plataforma diseñada para transformar datos en decisiones.\n"
            "Conecta visualizaciones, modelos predictivos y análisis exploratorio en un solo lugar.\n"
            "Ideal para proyectos logísticos, comerciales o académicos."
        )

    elif slide == 2:
        st.subheader("¿Qué puedo hacer?")
        st.write(
            "- Explorar datos con filtros dinámicos\n"
            "- Calcular métricas clave como tasa de retención o demoras\n"
            "- Visualizar ventas por región, tipo de envío o categoría\n"
            "- Detectar patrones para optimizar decisiones"
        )

    elif slide == 3:
        st.subheader("¿Qué incluye la parte de predicción?")
        st.write(
            "Utiliza modelos de machine learning para predecir:\n"
            "- El tipo de entrega de un pedido\n"
            "- El impacto del volumen o del estado en los tiempos de envío\n"
            "- Las categorías con mayor rotación o problemas logísticos"
        )

    elif slide == 4:
        st.subheader("¿Cómo empezar?")
        st.write(
            "1. Ve al menú lateral y elige la opción Exploración de Datos\n"
            "2. Filtra por estado, volumen o tipo de envío\n"
            "3. Interpreta las gráficas y guarda tus insights\n"
            "4. Usa la sección de Predicción para anticiparte a problemas"
        )

    elif slide == 5:
        st.subheader("Quinta sección")
        st.write(
            "Aquí puedes agregar contenido adicional, instrucciones avanzadas, créditos u otra información relevante."
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
