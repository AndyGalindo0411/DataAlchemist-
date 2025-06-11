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
            color: #5B8ae6;
            font-size: {title_size};
            font-weight: bold;
            margin-bottom: 1rem;
            text-align: {title_align};
        ">
            {title}
        </h2>
        <div style="
            color: #0d0d85;
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
def vista_conclusion():
    # Todas las tarjetas usan diseño vertical ahora
    render_slide_vertical(
        title="Aumentar Retención",
        description="Implementar el modelo predictivo para los Tiempos de Entrega, para que se priorice las categorías logísticamente eficientes y etiquetar productos elegibles para entregas rápidas y promociones específicas.",
        image=f"data:image/gif;base64,{load_image_base64('Imagenes\Imagen_Conclusion1.png')}"
    )
    render_slide_vertical(
        title="Mejorar la Retención Permitirá",
        description="Reducir costos operativos y de adquisición. Aumentando la recompra y teniendo estabilidad de ingresos mientras se fortalece la lealtad y el posicionamiento de la marca.",
        image=f"data:image/png;base64,{load_image_base64('Imagenes\Imagen_Conclusion2.png')}"
    )
    render_slide_vertical(
        title="Pero los datos no son una sentencia: Son Una Oportunidad.",
        description="Danu Shop, no solo vende productos, hace una promeda de calidad. La baja retención no es el final de la historia, sino el inicio de un capítulo más brillante para Danu Shop.",
        image=f"data:image/png;base64,{load_image_base64('Imagenes\Imagen_Conclusion3.png')}",
        title_size="28px"
    )
