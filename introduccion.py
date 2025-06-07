import streamlit as st  # type: ignore

def vista_introduccion():
    # === Título principal con HTML personalizado ===
    st.markdown("""
        <h2 style='text-align: center; color: white;'>
            Partial Shading <span style='color:#00FFAA;'>Re-estimation</span>
        </h2>
    """, unsafe_allow_html=True)

    # === Botones de navegación del carrusel ===
    col_left, _, col_right = st.columns([1, 8, 1])
    with col_left:
        if st.button("⬅ Shift left"):
            st.session_state.slide = st.session_state.get("slide", 0) - 1
    with col_right:
        if st.button("Shift right ➡"):
            st.session_state.slide = st.session_state.get("slide", 0) + 1

    # === Lista de slides (tarjetas con imágenes y objetos) ===
    slides = [
        {
            "title": "South",
            "objects": {"buildings": 2, "trees": 2, "pole": 1},
            "image_path": "Imagenes/1.png"
        },
        {
            "title": "East",
            "objects": {"buildings": 5, "trees": 5, "wall": 1, "pole": 3},
            "image_path": "Imagenes/2.png"
        },
        {
            "title": "North",
            "objects": {"trees": 4, "wall": 1, "pole": 6},
            "image_path": "Imagenes/3.png"
        }
    ]

    # === Selección del slide actual de forma circular ===
    index = st.session_state.get("slide", 0) % len(slides)
    slide = slides[index]

    # === Estilo personalizado para tarjeta neon púrpura ===
    st.markdown("""
        <style>
        .card-container {
            max-width: 450px;
            margin: auto;
            border-radius: 16px;
            padding: 0px;
            box-shadow: 0px 0px 16px 6px #f000ff;
            background-color: #30003b;
            color: white;
            overflow: hidden;
            font-family: 'Segoe UI', sans-serif;
        }
        .card-title {
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            padding: 10px 0;
            color: #ffffff;
        }
        .card-subtitle {
            font-size: 16px;
            font-weight: bold;
            margin: 15px 0 5px 0;
            padding-left: 20px;
        }
        .card-list {
            list-style: none;
            padding-left: 25px;
            font-size: 15px;
            margin-bottom: 20px;
        }
        .card-list li {
            margin: 4px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # === Tarjeta renderizada con contenido dinámico ===
    st.markdown(f"""
        <div class="card-container">

            <!-- Imagen superior de la tarjeta -->
            <img src="{slide['image_path']}" 
                 style="width: 100%; border-top-left-radius: 16px; border-top-right-radius: 16px;">

            <!-- Título de la tarjeta (ej. South) -->
            <div class="card-title">{slide['title']}</div>

            <!-- Subtítulo "Objects Detected" -->
            <div class="card-subtitle">OBJECTS DETECTED</div>

            <!-- Lista dinámica de objetos detectados -->
            <ul class="card-list">
                {"".join([f"<li>{k} : {v}</li>" for k, v in slide['objects'].items()])}
            </ul>

        </div>
    """, unsafe_allow_html=True)
