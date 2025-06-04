from pathlib import Path
import streamlit as st  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
import streamlit.components.v1 as components  # type: ignore

from inicio import cargar_datos, aplicar_filtros, calcular_kpis, mostrar_scatter_entregas_rapidas
from inicio import mostrar_linea_distribucion_entregas
from inicio import grafica_barra_horizontal_retencion


def vista_inicio():
    # === Estilos personalizados mejorados ===
    st.markdown("""
    <style>
    .block-container { padding-top: 3rem !important; }
    .titulo-principal {
        font-size: 40px;
        font-weight: 900;
        margin-bottom: 0.25rem;
    }
    .subtitulo {
        font-size: 22px;
        font-weight: 500;
        color: #444;
        margin-bottom: 2rem;
    }
    .kpi-container {
        display: flex;
        justify-content: center;
        flex-wrap: nowrap;
        gap: 1.5rem;
        overflow-x: hidden;
    }
    .kpi-box {
        background-color: #f8f9fa;
        border-radius: 16px;
        padding: 2rem 1.5rem;
        width: 230px;
        height: 200px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        word-wrap: break-word;
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
    .kpi-categoria {
        font-size: clamp(18px, 3vw, 28px);
        font-weight: 800;
        line-height: 1.2;
        word-wrap: break-word;
        white-space: normal;
    }
    .kpi-box:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
    }
    .up { color: green; }
    .down { color: red; }
    .divider {
        margin: 2.5rem 0 1.5rem 0;
        border-top: 2px solid #d3d3d3;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
<div style='text-align: left; padding-bottom: 1rem;'>
    <span style='font-size: 40px; font-weight: 900;'>Danu Shop</span>
    <span style='font-size: 24px; font-weight: 500; color: #444;'> - Panel de Indicadores Clave y Estratégicos</span>
</div>
""", unsafe_allow_html=True)

    df, error = cargar_datos()
    if error:
        st.warning(error)
        return

    st.session_state["df_upd"] = df

    with st.sidebar.expander("Filtros", expanded=True):
        categorias = ['Todos'] + sorted(df['categoria_nombre_producto'].dropna().unique().tolist())
        categoria_seleccionada = st.selectbox("Categoría", categorias)

        estados = ['Todos'] + sorted(df['estado_del_cliente'].dropna().unique().tolist())
        estado_seleccionado = st.selectbox("Estado", estados)

        tipo_entrega = st.selectbox("Tipo de Entrega", [
            "De (0-30 días)",
            "Prime (0–3 días)",
            "Express (4–7 días)",
            "Regular (8–30 días)"
        ])

    df_filtrado, df_estado = aplicar_filtros(df, categoria_seleccionada, estado_seleccionado)
    kpis = calcular_kpis(df, df_filtrado, df_estado, tipo_entrega, categoria_seleccionada, estado_seleccionado)

    st.markdown(f"""
<div class='kpi-container'>
    <div class='kpi-box'>
        <div class='kpi-title'>Tasa de Retención ({categoria_seleccionada})</div>
        <div class='kpi-value'>{kpis['retencion_cat']:.2f} %</div>
        <div class='kpi-delta {"up" if kpis['retencion_cat'] >= 3 else "down"}'>
            {"⬆ Retención superior al ideal" if kpis['retencion_cat'] >= 3 else "⬇ Retención inferior al ideal"}
        </div>
    </div>
    <div class='kpi-box'>
        <div class='kpi-title'>{kpis['titulo_kpi']}</div>
        <div class='kpi-value'>{kpis['promedio_filtrado']}</div>
        <div class='kpi-delta {"up" if kpis['promedio_filtrado'] < 7 else "down"}'>
            {"Ideal < 7 días" if kpis['promedio_filtrado'] < 7 else "Excede lo ideal (> 7 días)"}
        </div>
    </div>
    <div class='kpi-box'>
        <div class='kpi-title'>Entregas Rápidas en Alto Volumen</div>
        <div class='kpi-value'>{kpis['porcentaje_rapidas']:.2f} %</div>
        <div class='kpi-delta up'>Volumen alto entregado ≤ 7 días</div>
    </div>
    <div class='kpi-box'>
        <div class='kpi-title'>Top Categoría en {estado_seleccionado}</div>
        <div class='kpi-value kpi-categoria'>{kpis['top_categoria']}</div>
        <div class='kpi-delta up'>{kpis['ventas_top']} ventas</div>
    </div>
</div>
""", unsafe_allow_html=True)
    
    # === FILA: Distribución de Entregas + Top Categorías ===
    col1, col2 = st.columns([0.8,1])

    # Gráfica de Distribución de Entregas
    with col1:
        fig_linea = mostrar_linea_distribucion_entregas(kpis["dias_filtrados"], kpis["rango"])
        html_linea = fig_linea.to_html(full_html=False, include_plotlyjs='cdn')
        components.html(f"""
            <div style="
                box-shadow: 0px 12px 30px rgba(0, 0, 0, 0.4);
                border-radius: 16px;
                padding: 10px 10px 20px 10px;
                background-color: white;
                width: 100%;
                margin: auto;
            ">
                <div style="
                    font-size: 18px;
                    font-weight: 600;
                    text-align: center;
                    color: black;
                    margin-bottom: 10px;
                    font-family: Arial, sans-serif;
                ">
                    Distribución de Entregas
                </div>
                {html_linea}
            </div>
        """, height=450)

    # Gráfica de Top Categorías
    with col2:
        top5 = df_estado['categoria_nombre_producto'].value_counts().head(5).reset_index()
        top5.columns = ['Categoría', 'Ventas']

        fig_top5 = px.bar(
            top5,
            x='Categoría',
            y='Ventas',
            color='Categoría',
            color_discrete_sequence=["#040959"] * 5
        )

        fig_top5.update_traces(
            marker_line=dict(color='black', width=1.5),
            hovertemplate='<b>%{x}</b><br>Ventas: %{y}<extra></extra>',
        )

        fig_top5.update_layout(
            title=None,
            xaxis_title="Categoría",
            yaxis_title="Ventas",
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False,
            height=300,
            #width=600, 
            margin=dict(t=40, b=120, l=60, r=100),
            xaxis=dict(
                tickangle=-20,
                tickfont=dict(size=11),
                automargin=True,
            ),
            yaxis=dict(
                tickfont=dict(size=12)
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Arial"
            )
        )

        html_top5 = fig_top5.to_html(full_html=False, include_plotlyjs='cdn')
        components.html(f"""
            <div style="
                box-shadow: 0px 12px 30px rgba(0, 0, 0, 0.4);
                border-radius: 16px;
                padding: 10px;
                background-color: white;
                width: 90%;
                margin: auto;
            ">
                <div style="
                    font-size: 18px;
                    font-weight: 600;
                    text-align: center;
                    color: black;
                    margin-bottom: 10px;
                    font-family: Arial, sans-serif;
                ">
                    Top Categorías en {estado_seleccionado}
                </div>
                {html_top5}
            </div>
        """, height=600)