from pathlib import Path
import streamlit as st  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
import streamlit.components.v1 as components  # type: ignore

from inicio import cargar_datos, aplicar_filtros, calcular_kpis
from inicio import obtener_top5_top_categorias
from inicio import mostrar_linea_distribucion_entregas
from inicio import mostrar_dispersion_volumen_vs_flete_filtrado  # ✅ Asegúrate de tener esto

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
        padding: 1.2rem 1rem;
        width: 230px;
        height: 210px;
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
    .kpi-ventas-texto {
    font-size: 16px;      /* o prueba con 15px */
    font-weight: 600;
    margin-top: -10px;
    }
    .kpi-categoria-ajustada {
    font-size: 18px;    /* o 20px si quieres más énfasis */
    font-weight: 700;
    color: black;
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

    df, error = cargar_datos()
    if error:
        st.warning(error)
        return

    st.session_state["df_upd"] = df

    st.markdown("""
        <style>
        /* Estilo visual para el botón switch */
        [data-testid="stSidebar"] .stToggleSwitch label {
            font-weight: 600;
            font-size: 14px;
            color: #040959;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # === SWITCH para cambiar de Danu Shop a Predicción ===
    # === SWITCH para cambiar de Danu Shop a Predicción ===
    switch_estado = st.sidebar.toggle("Dashboard sin usar el modelo", value=False, help="Activa el switch para ver el dashboard con el modelo")

    if switch_estado:
        st.session_state.seccion_activa = "Predicción"
        st.rerun()  # ✅ Esta es la función correcta y actual para recargar

    with st.sidebar.expander("Filtros", expanded=True):
        categorias = ['Todos'] + sorted(df['categoria_de_productos'].dropna().unique().tolist())
        categoria_seleccionada = st.selectbox("Categoría", categorias)

        tipo_entrega = st.selectbox("Tipo de Entrega", [
            "De (0-30 días)",
            "Prime (0–3 días)",
            "Express (4–7 días)",
            "Regular (8–30 días)"
        ])

        # === NUEVOS FILTROS SOLICITADOS ===
        regiones = ['Todos'] + sorted(df['region'].dropna().unique().tolist())
        region_seleccionada = st.selectbox("Región", regiones)

        # Crear selector de fecha en formato Mes - Año
        df['orden_compra_timestamp_fecha'] = pd.to_datetime(df['orden_compra_timestamp_fecha'], errors='coerce')
        fechas_unicas = df['orden_compra_timestamp_fecha'].dropna().dt.to_period('M').drop_duplicates().sort_values()
        fechas_formato = ['Todos'] + fechas_unicas.astype(str).str.replace('-', ' - ', regex=False).tolist()

        fecha_seleccionada = st.selectbox("Fecha (Mes - Año)", fechas_formato)
        fecha_periodo = None if fecha_seleccionada == 'Todos' else fecha_seleccionada.replace(" - ", "-")  # Convertir a formato 'YYYY-MM'

        # Aplicar filtros con fecha incluida
        df_filtrado, df_region = aplicar_filtros(
            df,
            categoria_seleccionada,
            region_seleccionada,
            tipo_entrega,
            fecha_periodo
        )

        # Calcular KPIs
        kpis = calcular_kpis(
            df,
            df_filtrado,
            df_region,
            tipo_entrega,
            categoria_seleccionada,
            region_seleccionada
        )

    # === Mostrar título y filtros en la misma línea ===
    filtros_activos = []

    if categoria_seleccionada != "Todos":
        filtros_activos.append(f"Categoría: {categoria_seleccionada}")
    if tipo_entrega != "De (0-30 días)":
        filtros_activos.append(f"Entrega: {tipo_entrega}")
    if region_seleccionada != "Todos":
        filtros_activos.append(f"Región: {region_seleccionada}")
    if fecha_periodo is not None:
        filtros_activos.append(f"Fecha: {fecha_seleccionada}")

    st.markdown("""
    <style>
    .encabezado-con-filtros {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .titulo-linea {
        display: flex;
        align-items: baseline;
        gap: 10px;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .titulo-principal {
        font-size: 80px;
        font-weight: 900;
        color: black;
        margin: 0;
    }
    .subtitulo {
        font-size: 40px;
        font-weight: 800;
        color: #444;
        margin: 0;
    }
    .chip-container {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 0.2rem;
    }
    .chip {
        background-color: #white; /* Fondo azul claro */
        border-radius: 30px;
        padding: 6px 14px;
        font-size: 14px;
        font-weight: 500;
        color: #040959; /* Color de Texto*/
        border: 1px solid #040959;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

    # === Render del bloque con título y chips ===
    st.markdown(f"""
    <div class="encabezado-con-filtros">
        <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 1.5rem;">
            <span style="font-size: 30px; font-weight: 900; color: black;">Danu Shop</span>
            <span style="font-size: 20px; font-weight: 500; color: #444;">- Panel de Indicadores Clave y Estratégicos</span>
        </div>
        {"<div class='chip-container'>" + "".join([f"<div class='chip'>{filtro}</div>" for filtro in filtros_activos]) + "</div>" if filtros_activos else ""}
    </div>  
    """, unsafe_allow_html=True)

    st.markdown(f"""
<div class='kpi-container'>
    <div class='kpi-box'>
        <div class='kpi-title'>Tasa de Retención</div>
        <div class='kpi-value'>{kpis['retencion_cat']:.2f} %</div>
        <div class='kpi-delta {"up" if kpis['retencion_cat'] >= 3 else "down"}'>
            {"⬆ Retención superior al ideal" if kpis['retencion_cat'] >= 3 else "⬇ Retencion inferior a benchmark (20%)"}
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
        <div class='kpi-title'>Volumen Promedio</div>
        <div class='kpi-value'>{int(kpis['volumen_promedio']):,} cm³</div>
        <div class='kpi-delta {"up" if kpis['volumen_promedio'] >= 0 else "down"}'>
            Volumen medio
        </div>
    </div>
    <div class='kpi-box'>
        <div class='kpi-title'>Núm de Pedidos</div>
        <div class='kpi-value'>
            <span style="font-weight:900; font-size:32px;">{kpis['num_pedidos']:,}</span>
            <span style="font-size:18px; font-weight:600; margin-left:8px;">pedidos</span>
        </div>
        <div class='kpi-delta' style="margin-top: 6px;">
            Por {categoria_seleccionada if categoria_seleccionada != 'Todos' else 'todas las categorías'}
        </div>
    </div>
    </div>
</div>
""", unsafe_allow_html=True)
    
    # === FILA: Distribución + Dispersión a la izquierda, Top Categorías a la derecha ===
    # === UNIFICADO: Las tres gráficas en una sola tarjeta ===
    # Preparamos las gráficas individualmente
    fig_linea = mostrar_linea_distribucion_entregas(kpis["dias_filtrados"], kpis["rango"])
    html_linea = fig_linea.to_html(full_html=False, include_plotlyjs='cdn')

    fig_dispersion = mostrar_dispersion_volumen_vs_flete_filtrado(df, categoria_seleccionada, tipo_entrega)  # type: ignore
    html_dispersion = fig_dispersion.to_html(full_html=False, include_plotlyjs='cdn')

    top5 = obtener_top5_top_categorias(df, region_seleccionada, fecha_periodo, tipo_entrega)
    top5.columns = ['Categoría', 'Ventas']
    fig_top5 = px.bar(
        top5,
        x='Categoría',
        y='Ventas',
        color='Categoría',
        color_discrete_sequence=["#265cbb"] * 5
    )
    fig_top5.update_traces(
        marker_line=dict(color='#265cbb', width=1.5),
        hovertemplate='<b>%{x}</b><br>Pedidos: %{y}<extra></extra>',
    )
    fig_top5.update_layout(
        title=None,
        xaxis_title="Categoría",
        yaxis_title="Pedidos",
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        height=250,   # Igual que distribución
        width=700,    # Ajustado al tamaño izquierdo
        margin=dict(t=0, b=80, l=100, r=60),
        xaxis=dict(tickangle=-20, tickfont=dict(size=11), automargin=True),
        yaxis=dict(tickfont=dict(size=12)),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial")
    )

    # Antes del HTML
    if region_seleccionada != 'Todos' and fecha_periodo != 'Todos':
        titulo_top = f"Top Categorías"
    elif region_seleccionada != 'Todos':
        titulo_top = f"Top Categorías"
    elif fecha_periodo != 'Todos':
        titulo_top = f"Top Categorías"
    else:
        titulo_top = "Top Categorías"

    html_top5 = fig_top5.to_html(full_html=False, include_plotlyjs='cdn')

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
    flex-direction: column;
    gap: 30px;
    overflow: hidden;
">

    <!-- FILA SUPERIOR: Top Categorías y Volumen vs Costo de Flete -->
    <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 30px;">

        <!-- IZQUIERDA: Top Categorías -->
        <div style="flex: 1; max-width: 48%;">
            <div style="
                font-size: 18px;
                font-weight: 600;
                text-align: center;
                color: black;
                margin-bottom: 10px;
                font-family: Arial, sans-serif;
            ">{titulo_top}</div>
            {html_top5}
        </div>

        <!-- DERECHA: Volumen vs Costo de Flete -->
        <div style="flex: 1; max-width: 48%;">
            <div style="
                font-size: 18px;
                font-weight: 600;
                text-align: center;
                color: black;
                margin-bottom: 10px;
                font-family: Arial, sans-serif;
            ">Volumen vs Costo de Flete</div>
            {html_dispersion}
        </div>
    </div>

    <!-- FILA INFERIOR: Distribución de Entregas -->
    <div style="width: 100%; margin-top: -10px;">
        <div style="
            font-size: 18px;
            font-weight: 600;
            text-align: center;
            color: black;
            margin-bottom: -2px;
            font-family: Arial, sans-serif;
        ">Distribución de Entregas</div>
        {html_linea}
    </div>

</div>
""", height=595, scrolling=False)

