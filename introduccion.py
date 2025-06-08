import streamlit as st  # type: ignore
import streamlit.components.v1 as components  # type: ignore
import base64

# === CSS para ocultar menú lateral ===
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# === Función para codificar imagen local a base64 ===
def load_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# === Tarjeta VERTICAL para TODAS las slides
def render_slide_vertical(title, description, image, title_align="center", title_size="32px"):
    html = f"""
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Quicksand&display=swap" rel="stylesheet">
    </head>
    <div style="
        background-color: white;
        border: 2px solid #ccc;
        border-radius: 20px;
        box-shadow: 0px 4px 55px rgba(0,0,0,0.2);
        padding: 3rem 2rem;
        margin: 2rem auto;
        max-width: 800px;
        font-family: 'Quicksand', sans-serif;
        text-align: center;
    ">
        <div style="margin-bottom: 2rem;">
            <img src="{image}" style="
                max-width: 320px;
                width: 100%;
                height: auto;
                object-fit: contain;
                border-radius: 12px;
            ">
        </div>
        <h2 style="
            color: red;
            font-size: {title_size};
            font-weight: bold;
            margin-bottom: 1rem;
            text-align: {title_align};
        ">
            {title}
        </h2>
        <div style="
            color: #ff69b4;
            font-size: 20px;
            line-height: 1.6;
            max-width: 90%;
            margin: 0 auto;
        ">
            {description}
        </div>
    </div>
    """
    components.html(html, height=800)


# === Vista principal
def vista_introduccion():
    # Todas las tarjetas usan diseño vertical ahora
    render_slide_vertical(
        title="Maya Angelou",
        description="He aprendido que la gente olvidará lo que dijiste, olvidará lo que hiciste, pero nunca olvidará cómo los hiciste sentir.",
        image=f"data:image/gif;base64,{load_image_base64('Imagenes/Imagen3 (2).gif')}"
    )
    render_slide_vertical(
        title="Benchmark",
        description="Una empresa de E-Commerce tiene un benchmark de retención entre el 20% y 30%.",
        image=f"data:image/png;base64,{load_image_base64('Imagenes/Imagen2.png')}"
    )
    render_slide_vertical(
        title="Un Cliente Satisfecho NO Solo Vuelve... También Recomienda.",
        description="La retención de clientes es fundamental para evaluar la fidelidad de los clientes y la efectividad de la estrategia de recompra.",
        image=f"data:image/png;base64,{load_image_base64('Imagenes/Imagen1.png')}",
        title_size="28px"
    )

    # Espaciado
    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    espacio_izq, centro, espacio_der = st.columns([2, 2, 2])
    with centro:
        if st.button("Descubre Danu Shop", key="boton_danu", use_container_width=True):
            st.session_state.seccion_activa = "Danu Shop"
            st.rerun()