import streamlit as st  # type: ignore
import streamlit.components.v1 as components  # type: ignore

# Función general para renderizar cada tarjeta personalizada
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
    # Se aumenta la altura para que soporte texto más largo sin cortar
    components.html(html, height=550)

# Vista principal
def vista_introduccion():
    # Slide 1
    render_slide(
        title="Maya Angelou",
        description="He aprendido que la gente olvidará lo que dijiste, olvidará lo que hiciste, pero nunca olvidará cómo los hiciste sentir.",
        image="https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif",
        image_on_left=False,
        text_align="right",
        title_align="center",
        margin_left="300px"
    )

    # Slide 2
    render_slide(
        title="Benchmark",
        description="Una empresa de E-Commerce tiene un benchmark de retención entre el 20% y 30%.",
        image="https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif",
        image_on_left=True,
        text_align="left",
        title_align="left",
        margin_left="0"
    )

    # Slide 3 (título largo y ajustado)
    render_slide(
        title="Un Cliente Satisfecho NO Solo Vuelve... También Recomienda.",
        description="La retención de clientes es fundamental para evaluar la fidelidad de los clientes y la efectividad de la estrategia de recompra.",
        image="https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif",
        image_on_left=False,
        text_align="right",
        title_align="center",
        margin_left="450px",
        title_size="28px"  # ⬅️ un poco más pequeño para caber mejor
    )
