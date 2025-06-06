import streamlit as st  # type: ignore
import plotly.graph_objects as go  # type: ignore
import plotly.express as px  # type: ignore
import pandas as pd  # type: ignore
import streamlit.components.v1 as components  # type: ignore
from prediccion import cargar_base_proyeccion, calcular_retencion

def vista_prediccion():
    df_proy, error = cargar_base_proyeccion()
    if error:
        st.error(error)
        return

    # === Estilos heredados de inicioFront
    st.markdown("""
    <style>
    .titulo-principal {
        font-size: 28px;
        font-weight: 900;
        margin-bottom: 0.25rem;
    }
    .kpi-container {
        display: flex;
        justify-content: center;
        flex-wrap: nowrap;
        gap: 3rem;
        overflow-x: hidden;
        margin-bottom: 0rem;
    }
    .kpi-box {
        background-color: #f8f9fa;
        border-radius: 16px;
        padding: 1.2rem 1rem;
        width: 250px;
        height: 150px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        transition: all 0.3s ease-in-out;
        box-shadow: none;
    }
    .kpi-title {
        font-size: 15px;
        color: #333;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 900;
        color: #000;
        margin-bottom: 0.5rem;
    }
    .kpi-delta {
        font-size: 13px;
        font-weight: 500;
        line-height: 1.2;
    }
    .kpi-box:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
    }
    .up { color: green; }
    .down { color: red; }
    </style>
    """, unsafe_allow_html=True)

    # === Encabezado y filtro
    col_titulo, col_filtro = st.columns([3, 1])
    with col_titulo:
        st.markdown("<div class='titulo-principal'>Predicción de Retención de Clientes</div>", unsafe_allow_html=True)
    with col_filtro:
        tipo_envio = st.selectbox(
            " ",
            ("Todas (0-30 días)", "Prime (0-3 días)", "Express (4-7 días)", "Regular (8-30 días)"),
            label_visibility="collapsed"
        )

    # === Filtrado
    if tipo_envio == "Prime (0-3 días)":
        df_filtrado = df_proy[df_proy['entrega_simulada_dias'].between(0, 3)]
        rango_dias = range(0, 4)
    elif tipo_envio == "Express (4-7 días)":
        df_filtrado = df_proy[df_proy['entrega_simulada_dias'].between(4, 7)]
        rango_dias = range(4, 8)
    elif tipo_envio == "Regular (8-30 días)":
        df_filtrado = df_proy[df_proy['entrega_simulada_dias'].between(8, 30)]
        rango_dias = range(8, 31)
    else:
        df_filtrado = df_proy[df_proy['entrega_simulada_dias'].between(0, 30)]
        rango_dias = range(0, 31)

    retenidos_proy, total_proy, retencion_proy = calcular_retencion(df_filtrado)
    retenidos_total, total_clientes_total, retencion_total = calcular_retencion(df_proy)

    retencion_actual_dict = {
        "Todas (0-30 días)": 2.95,
        "Prime (0-3 días)": 0.25,
        "Express (4-7 días)": 0.73,
        "Regular (8-30 días)": 1.97
    }
    retencion_actual = retencion_actual_dict.get(tipo_envio, 2.95)
    tasa_retencion_global_segmento = (retenidos_proy / total_clientes_total) * 100 if total_clientes_total > 0 else 0
    delta_ret = tasa_retencion_global_segmento - retencion_actual

    entrega_actual = 10
    mediana_entrega = round(df_filtrado['entrega_simulada_dias'].dropna().median())
    mejora_entrega = entrega_actual - mediana_entrega
    unidad_dias = "día" if abs(mejora_entrega) == 1 else "días"

    volumen_median = round(df_filtrado['volumen'].dropna().median(), 2)
    volumen_total_median = round(df_proy['volumen'].dropna().median(), 2)

    # === KPIs visuales (formato heredado de inicioFront)
    st.markdown(f"""
    <div class='kpi-container'>
        <div class='kpi-box'>
            <div class='kpi-title'>Tasa de Retención</div>
            <div class='kpi-value'>{tasa_retencion_global_segmento:.2f} %</div>
            <div class='kpi-delta {"up" if delta_ret >= 0 else "down"}'>
                {"⬆ Mejora de " if delta_ret >= 0 else "⬇ Caída de "} {abs(delta_ret):.2f} puntos
            </div>
        </div>
        <div class='kpi-box'>
            <div class='kpi-title'>Mediana de Entrega</div>
            <div class='kpi-value'>{mediana_entrega} días</div>
            <div class='kpi-delta {"up" if mejora_entrega > 0 else "down"}'>
                {"⬆ Mejora de" if mejora_entrega > 0 else "⬇ Peor en"} {abs(mejora_entrega)} {unidad_dias}
            </div>
        </div>
        <div class='kpi-box'>
            <div class='kpi-title'>Volumen Logístico</div>
            <div class='kpi-value'>{volumen_median:,.0f} cm³</div>
            <div class='kpi-delta up'>Distribución eficiente</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # === GRÁFICA 1: Distribución
    dias = df_filtrado['entrega_simulada_dias'].dropna()
    conteo_dias = dias.value_counts().sort_index()
    conteo_dias = pd.Series(index=rango_dias, dtype=int).fillna(0).add(conteo_dias, fill_value=0).astype(int)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=conteo_dias.index,
        y=conteo_dias.values,
        mode="lines+markers",
        fill='tozeroy',
        line=dict(color="#0811C1", width=3),
        hovertemplate="Día %{x}<br>Cantidad: %{y}<extra></extra>"
    ))
    fig1.update_layout(
        height=360,
        width=700,
        title=None,
        xaxis_title="Días de Entrega",
        yaxis_title="Cantidad de Entregas",
        template="simple_white",
        margin=dict(t=0, b=100, l=100, r=100)
        #margin=dict(t=10, b=60, l=60, r=30)
    )
    html_fig1 = fig1.to_html(full_html=False, include_plotlyjs='cdn')

    # === Clasificar tipo de entrega (Prime, Express, Regular)
    df_plot = df_filtrado.dropna(subset=['volumen', 'costo_de_flete'])
    df_plot['tiempo_total_entrega_dias'] = pd.to_numeric(df_plot['tiempo_total_entrega_dias'], errors='coerce')

    df_plot['tipo_entrega'] = pd.cut(
        df_plot['tiempo_total_entrega_dias'],
        bins=[-1, 3, 7, 30],
        labels=["Prime", "Express", "Regular"]
    )

    # === Gráfico con color por tipo_entrega
    fig2 = px.scatter(
        df_plot,
        x="volumen",
        y="costo_de_flete",
        color="tipo_entrega",
        opacity=0.7,
        labels={
            "volumen": "Volumen (cm³)",
            "costo_de_flete": "Costo de Flete ($)",
            "tipo_entrega": "Tipo de Entrega"
        },
        color_discrete_map={
            "Prime": "#0511F2",     # Azul oscuro
            "Express": "#353EE9",   # Azul medio
            "Regular": "#5A61E2"    # Azul claro
        }
    )

    fig2.update_traces(marker=dict(size=7, line=dict(width=0.5, color='black')))

    fig2.update_layout(
        height=360,
        width=640,
        xaxis_title="Volumen",
        yaxis_title="Costo de Flete",
        template="simple_white",
        margin=dict(t=0, b=100, l=100, r=100),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    html_fig2 = fig2.to_html(full_html=False, include_plotlyjs='cdn')

    # === TARJETA CONTENEDORA DE GRÁFICAS (estilo inicioFront)
    components.html(f"""
    <div style="
        box-shadow: 0px 12px 30px rgba(0, 0, 0, 0.4);
        border-radius: 16px;
        padding: 20px;
        background-color: white;
        width: 100%;
        max-width: 1300px;
        margin: auto;
        display: flex;
        flex-direction: row;
        gap: 30px;
    ">

        <!-- GRÁFICA: Distribución de Entregas -->
        <div style="flex: 1; max-width: 50%;">
            <div style="
                font-size: 18px;
                font-weight: 600;
                text-align: center;
                color: black;
                margin-bottom: 0px;
                font-family: Arial, sans-serif;
            ">Distribución de Entregas</div>
            {html_fig1}
        </div>

        <!-- GRÁFICA: Volumen vs Costo de Flete -->
        <div style="flex: 1; max-width: 50%;">
            <div style="
                font-size: 18px;
                font-weight: 600;
                text-align: center;
                color: black;
                margin-bottom: 10px;
                font-family: Arial, sans-serif;
            ">Volumen vs Costo de Flete</div>
            {html_fig2}
        </div>
    </div>
    """, height=450, scrolling=False)
