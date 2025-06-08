import streamlit as st # type: ignore
import streamlit.components.v1 as components # type: ignore
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


# === Tarjetas (igual que antes)
def render_slide(title, description, image, image_on_left=False, text_align="right", title_align="center", margin_left="300px", title_size="32px"):
    html = f"""
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Quicksand&display=swap" rel="stylesheet">
    </head>
    <div style="
        background-color: white;
        border: 2px solid #ccc;
        border-radius: 20px;
        box-shadow: 0px 4px 55px rgba(0,0,0,0.2);
        padding: 2rem;
        margin: 2rem auto;
        max-width: 900px;
        font-family: 'Quicksand', sans-serif;
    ">
        <h2 style="
            text-align: {title_align};
            color: red;
            font-family: 'Quicksand', sans-serif;
            font-size: {title_size};
            font-weight: bold;
            margin-top: -20px;
            margin-left: {margin_left};
            word-break: break-word;
        ">
            {title}
        </h2>

        <div style="
            display: flex;
            flex-direction: {'row' if image_on_left else 'row-reverse'};
            align-items: stretch;
            gap: 2rem;
            height: 100%;
        ">
            <div style="
                flex: 2;
                color: #ff69b4;
                font-size: 25px;
                text-align: {text_align};
                font-family: 'Quicksand', sans-serif;
                line-height: 1.5;
                margin-top: -15px;
                display: flex;
                align-items: center;
            ">
                {description}
            </div>

            <div style="
                flex: 2;
                display: flex;
                align-items: flex-end;
                justify-content: center;
                height: 110px;
            ">
                <img src="{image}" style="
                    width: 100%;
                    height: 150%;
                    object-fit: cover;
                    border-radius: 12px;
                    margin-top: -200px;
                ">
            </div>
        </div>
    </div>
    """
    components.html(html, height=550)

# === Vista principal
def vista_introduccion():
    render_slide(
        title="Maya Angelou",
        description="He aprendido que la gente olvidará lo que dijiste, olvidará lo que hiciste, pero nunca olvidará cómo los hiciste sentir.",
        image="Imagenes/Imagen1.png",
        image_on_left=False
    )
    render_slide(
        title="Benchmark",
        description="Una empresa de E-Commerce tiene un benchmark de retención entre el 20% y 30%.",
        image="Imagenes/Imagen2.png",
        image_on_left=True,
        text_align="left",
        title_align="left",
        margin_left="0"
    )
    render_slide(
        title="Un Cliente Satisfecho NO Solo Vuelve... También Recomienda.",
        description="La retención de clientes es fundamental para evaluar la fidelidad de los clientes y la efectividad de la estrategia de recompra.",
        image="Imagenes/Imagen3.gif",
        margin_left="450px",
        title_size="28px"
    )

    # Espaciado
    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # Mostrar imagen como botón usando base64
    col = st.columns([2, 1, 2])[1]
    with col:
        img_base64 = load_image_base64("Imagenes/LogoDanu.jpeg")
        button_html = f"""
        <style>
        .hover-container {{
            position: relative;
            display: inline-block;
        }}
        .hover-container .hover-text {{
            visibility: hidden;
            width: 220px;
            background-color: #ff69b4; //cambiar el color
            color: white;
            text-align: center;
            border-radius: 8px;
            padding: 8px 12px;
            position: absolute;
            z-index: 1;
            bottom: 110%; /* arriba de la imagen */
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
            font-size: 13px;
            font-family: 'Quicksand', sans-serif;
        }}
        .hover-container:hover .hover-text {{
            visibility: visible;
            opacity: 1;
        }}
        </style>

        <form action="" method="post">
            <button type="submit" name="go_danu" style="border: none; background: none;">
                <div class="hover-container">
                    <img src="data:image/png;base64,{img_base64}" style="width: 80%; max-width: 100px;" alt="Ir a Danu Shop">
                    <div class="hover-text">Bienvenido a Danu Shop — Haz clic para empezar</div>
                </div>
            </button>
        </form>
        """
        st.markdown(button_html, unsafe_allow_html=True)


    # Detectar clic usando query_params simulados
    if st.query_params.get("go_danu") is not None:
        st.session_state.seccion_activa = "Danu Shop"
        st.rerun()
