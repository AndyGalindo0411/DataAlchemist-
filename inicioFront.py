from pathlib import Path
import streamlit as st  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
import streamlit.components.v1 as components  # type: ignore

from inicio import cargar_datos, aplicar_filtros, calcular_kpis, mostrar_scatter_entregas_rapidas

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
    .hover-card {
        background-color: red;
        width: 500px;
        height: 350px;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: box-shadow 0.3s ease, transform 0.3s ease;
    }

    .hover-card:hover {
        box-shadow: 0px 12px 30px rgba(0, 0, 0, 0.4);
        transform: scale(1.02);
    }            
    .visual-title {
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        color: #333;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='titulo-principal'>Danu Shop</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitulo'>Panel de Indicadores Clave y Estratégicos</div>", unsafe_allow_html=True)

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

    kpi_html = ""
    if kpis["ahorro_express"] is not None and kpis["ahorro_prime"] is not None:
        kpi_html += f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Ahorro vs Regular (Express)</div>
            <div class='kpi-value'>{kpis['ahorro_express']:.2f}%</div>
            <div class='kpi-delta up'>Entrega Express tiene menor costo</div>
        </div>
        <div class='kpi-box'>
            <div class='kpi-title'>Ahorro vs Regular (Prime)</div>
            <div class='kpi-value'>{kpis['ahorro_prime']:.2f}%</div>
            <div class='kpi-delta up'>Entrega Prime tiene menor costo</div>
        </div>
        """

    st.markdown(f"""
    <div class='kpi-container'>
        <div class='kpi-box'>
            <div class='kpi-title'>% Entregas Rápidas en Alto Volumen</div>
            <div class='kpi-value'>{kpis['porcentaje_rapidas']:.2f} %</div>
            <div class='kpi-delta up'>Volumen > p75 entregado en ≤ 7 días</div>
        </div>
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
            <div class='kpi-title'>Top Categoría en {estado_seleccionado}</div>
            <div class='kpi-value kpi-categoria'>{kpis['top_categoria']}</div>
            <div class='kpi-delta up'>{kpis['ventas_top']} ventas</div>
        </div>
    </div>
    """ + kpi_html, unsafe_allow_html=True)

    # === Visualizaciones Estilizadas ===
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<h3 class="visual-title">Visualizaciones Generales</h3>', unsafe_allow_html=True)

    # === Gráfico de dispersión de entregas rápidas ===
    st.markdown('<div class="visual-card">', unsafe_allow_html=True)
    fig_scatter = mostrar_scatter_entregas_rapidas(df_estado)
    fig_scatter.update_layout(width=350, height=260)
    st.plotly_chart(fig_scatter, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

    # === Pie Chart + Bar Chart Distribución ===
    col1, col2 = st.columns(2)

    with col1:
        df_retencion = pd.DataFrame({
            "Tipo de Cliente": ["Retenidos", "No Retenidos"],
            "Porcentaje": [kpis['retencion_cat'], kpis['no_retenidos_cat']]
        })

        fig_ret = px.pie(
            df_retencion, 
            values='Porcentaje', 
            names='Tipo de Cliente',
            color_discrete_map={"Retenidos": "#020873", "No Retenidos": "#9999aa"}
        )

        fig_ret.update_traces(
            marker=dict(colors=["#9999aa", "#020873"]),
            textinfo="none",  # Oculta el % dentro del gráfico
            hoverinfo="label+percent"  # Solo se ve en hover
        )

        fig_ret.update_layout(
            title=dict(
                text="Clientes Retenidos vs No Retenidos",
                x=0.1,
                font=dict(size=18, color="black")
           ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
            margin=dict(t=60, b=30, l=30, r=30),
            width=400, height=400,
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )
        html = fig_ret.to_html(full_html=False, include_plotlyjs='cdn')

        # Contenedor con sombra alrededor del gráfico
        components.html(f"""
            <div style="
                box-shadow: 0px 12px 30px rgba(0, 0, 0, 0.4);
                border-radius: 16px;
                padding: 10px;
                width: fit-content;
                margin: auto;
            ">
                {html}
            </div>
        """, height=450)
        #st.plotly_chart(fig_ret, use_container_width=False)
        st.markdown('</div>', unsafe_allow_html=True)


    with col2:
        st.markdown('<div class="visual-card">', unsafe_allow_html=True)
        st.markdown('<h4 class="visual-title">Distribución de Entregas</h4>', unsafe_allow_html=True)

        conteo_por_dia = kpis['dias_filtrados'].value_counts().sort_index()
        conteo_por_dia = pd.Series(index=kpis['rango'], dtype=int).fillna(0).add(conteo_por_dia, fill_value=0).astype(int)

        fig_dist = go.Figure(data=[
            go.Bar(
                x=conteo_por_dia.index,
                y=conteo_por_dia.values,
                marker_color='#4D4FFF'
            )
        ])
        fig_dist.update_layout(
            margin=dict(t=10, b=10, l=20, r=10),
            width=350, height=260
        )
        st.plotly_chart(fig_dist, use_container_width=False)
        st.markdown('</div>', unsafe_allow_html=True)

    # === Bar Chart – Top Categorías ===
    st.markdown('<div class="visual-card">', unsafe_allow_html=True)
    st.markdown(f'<h4 class="visual-title">Top Categorías en {estado_seleccionado}</h4>', unsafe_allow_html=True)

    top5 = df_estado['categoria_nombre_producto'].value_counts().head(5).reset_index()
    top5.columns = ['Categoría', 'Ventas']
    fig_top5 = px.bar(top5, x='Categoría', y='Ventas', text='Ventas')
    fig_top5.update_layout(
        margin=dict(t=10, b=10, l=20, r=10),
        width=600, height=260
    )
    st.plotly_chart(fig_top5, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.markdown("""
        <hr style='margin-top:12px;margin-bottom:4px;'>
        <p style='font-size:11px;text-align:center;margin:0;color:#444;'>
            Todos los derechos reservados<br><strong>DataAlchemist</strong>
        </p>
    """, unsafe_allow_html=True)
