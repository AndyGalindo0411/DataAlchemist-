# ================================
#           FRONTEND
# ================================

import streamlit as st # type: ignore
import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
from datos import cargar_datos, aplicar_filtros, calcular_kpis


def vista_inicio():
    # Estilos personalizados
    st.markdown("""
    <style>
    .block-container { padding-top: 3rem !important; }
    .titulo-principal { font-size: 36px; font-weight: bold; margin-bottom: 0.25rem; }
    .subtitulo { font-size: 20px; font-weight: 500; color: #444; margin-bottom: 2rem; }
    .kpi-box {
        background-color: #f8f9fa;
        border-radius: 12px;
        box-shadow: 0px 8px 30px rgba(0,0,0,0.25);
        padding: 1rem;
        width: 180px;
        height: 180px;
        text-align: center;
        margin: 0.5rem;
        display: inline-block;
        vertical-align: top;
    }
    .kpi-title { font-size: 13px; color: #555; margin-bottom: 4px; }
    .kpi-value { font-size: 22px; font-weight: 800; color: #111; }
    .kpi-delta { font-size: 12px; font-weight: 500; margin-top: 4px; color: green; }
    .up { color: green; } .down { color: red; }
    .divider { margin: 2rem 0 1rem 0; border-top: 2px solid #d3d3d3; }
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

    # Mostrar KPIs
    kpi_html = ""
    if kpis["ahorro_express"] is not None and kpis["ahorro_prime"] is not None:
        kpi_html += f"""
        <div class='kpi-box'>
            <div class='kpi-title'>Ahorro vs Regular (Express)</div>
            <div class='kpi-value'>{kpis['ahorro_express']:.2f}%</div>
            <div class='kpi-delta up'>Entrega Express cuesta menos</div>
        </div>
        <div class='kpi-box'>
            <div class='kpi-title'>Ahorro vs Regular (Prime)</div>
            <div class='kpi-value'>{kpis['ahorro_prime']:.2f}%</div>
            <div class='kpi-delta up'>Entrega Prime cuesta menos</div>
        </div>
        """

    st.markdown(f"""
<div style='display: flex; flex-wrap: wrap; justify-content: center;'>
    <div class='kpi-box'>
        <div class='kpi-title'>% Entregas Rápidas en Alto Volumen</div>
        <div class='kpi-value'>{kpis['porcentaje_rapidas']:.2f} %</div>
        <div class='kpi-delta'>Volumen > p75 entregado en ≤ 7 días</div>
    </div>
    <div class='kpi-box'>
        <div class='kpi-title'>Tasa de Retención ({categoria_seleccionada})</div>
        <div class='kpi-value'>{kpis['retencion_cat']:.2f} %</div>
        <div class='kpi-delta {"up" if kpis['retencion_cat'] >= 3 else "down"}'>{"⬆" if kpis['retencion_cat'] >= 3 else "⬇"} {abs(kpis['retencion_cat'] - 3):.2f}% desde 3%</div>
    </div>
    <div class='kpi-box'>
        <div class='kpi-title'>{kpis['titulo_kpi']}</div>
        <div class='kpi-value'>{kpis['promedio_filtrado']}</div>
        <div class='kpi-delta'>ideal < 7 días</div>
    </div>
    <div class='kpi-box'>
        <div class='kpi-title'>Top Categoría en {estado_seleccionado}</div>
        <div class='kpi-value'>{kpis['top_categoria']}</div>
        <div class='kpi-delta'>{kpis['ventas_top']} ventas</div>
    </div>
</div>
""" + kpi_html, unsafe_allow_html=True)

    # Visualizaciones
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### Visualizaciones Generales")
    colv1, colv2 = st.columns(2)
    with colv1:
        st.subheader("Clientes Retenidos vs No Retenidos")
        fig_r, ax_r = plt.subplots()
        ax_r.pie([kpis['retencion_cat'], kpis['no_retenidos_cat']],
                 labels=["Retenidos", "No Retenidos"],
                 autopct='%1.1f%%', colors=["#55d6be", "#329fbd"], startangle=90)
        ax_r.axis('equal')
        st.pyplot(fig_r)

    with colv2:
        st.subheader("Distribución de Entregas")
        conteo_por_dia = kpis['dias_filtrados'].value_counts().sort_index()
        conteo_por_dia = pd.Series(index=kpis['rango'], dtype=int).fillna(0).add(conteo_por_dia, fill_value=0).astype(int)
        fig_d, ax_d = plt.subplots(figsize=(12, 4))
        ax_d.bar(conteo_por_dia.index, conteo_por_dia.values, color='#4D4FFF', edgecolor='black')
        ax_d.set_xlabel("Días de Entrega")
        ax_d.set_ylabel("Cantidad de Pedidos")
        ax_d.set_xticks(list(kpis['rango']))
        ax_d.set_xlim(min(kpis['rango']), max(kpis['rango']))
        ax_d.grid(True, axis='y')
        st.pyplot(fig_d)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### Top 5 Categorías por Frecuencia de Ventas")
    st.markdown(f"Estado: **{estado_seleccionado}**")
    top5 = df_estado['categoria_nombre_producto'].value_counts().head(5)
    fig_t5, ax_t5 = plt.subplots(figsize=(8, 4))
    ax_t5.bar(top5.index, top5.values, color='#4D4FFF', edgecolor='black')
    ax_t5.set_xlabel("Categoría")
    ax_t5.set_ylabel("Número de Ventas")
    ax_t5.set_xticklabels(top5.index, rotation=45, ha='right')
    st.pyplot(fig_t5)

    st.sidebar.markdown("""
        <hr style='margin-top:12px;margin-bottom:4px;'>
        <p style='font-size:11px;text-align:center;margin:0;color:#444;'>
            Todos los derechos reservados<br><strong>DataAlchemist</strong>
        </p>
    """, unsafe_allow_html=True)
