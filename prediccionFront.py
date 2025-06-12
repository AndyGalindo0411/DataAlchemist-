import streamlit as st  # type: ignore
import plotly.graph_objects as go  # type: ignore
import plotly.express as px  # type: ignore
import pandas as pd  # type: ignore
import streamlit.components.v1 as components  # type: ignore
from prediccion import cargar_base_proyeccion, calcular_retencion

def vista_prediccion():
    # === SWITCH para volver a vista Danu Shop desde Predicción ===
    switch_estado = st.sidebar.toggle("Dashboard usando el modelo", value=True)

    if not switch_estado:
        st.session_state.seccion_activa = "Danu Shop"
        st.rerun()

    df_proy, error = cargar_base_proyeccion()
    if error:
        st.error(error)
        return

    # === Filtros desde el menú lateral ===
    with st.sidebar.expander("Filtros - Predicción", expanded=True):
        categorias = ['Todos'] + sorted(df_proy['categoria_de_productos'].dropna().unique().tolist())
        categoria_pred = st.selectbox("Categoría", categorias)

        regiones = ['Todos'] + sorted(df_proy['region'].dropna().unique().tolist())
        region_pred = st.selectbox("Región", regiones)

        tipo_envio = st.selectbox("Tipo de Entrega", [
            "Todas (0-30 días)",
            "Prime (0-3 días)",
            "Express (4-7 días)",
            "Regular (8-30 días)"
        ])

    # === Aplicar filtros ===
    df_filtrado = df_proy.copy()

    if categoria_pred != "Todos":
        df_filtrado = df_filtrado[df_filtrado["categoria_de_productos"] == categoria_pred]

    if region_pred != "Todos":
        df_filtrado = df_filtrado[df_filtrado["region"] == region_pred]

    if tipo_envio == "Prime (0-3 días)":
        df_filtrado = df_filtrado[df_filtrado['entrega_simulada_dias'].between(0, 3)]
        rango_dias = range(0, 4)
    elif tipo_envio == "Express (4-7 días)":
        df_filtrado = df_filtrado[df_filtrado['entrega_simulada_dias'].between(4, 7)]
        rango_dias = range(4, 8)
    elif tipo_envio == "Regular (8-30 días)":
        df_filtrado = df_filtrado[df_filtrado['entrega_simulada_dias'].between(8, 30)]
        rango_dias = range(8, 31)
    else:
        df_filtrado = df_filtrado[df_filtrado['entrega_simulada_dias'].between(0, 30)]
        rango_dias = range(0, 31)

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
    # === Estilo para chips de filtros
    st.markdown("""
    <style>
    .encabezado-con-filtros {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .chip-container {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 0.2rem;
    }
    .chip {
        background-color: #040959;
        border-radius: 30px;
        padding: 6px 14px;
        font-size: 14px;
        font-weight: 500;
        color: white;
        border: 1px solid #040959;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
    }
    .chip-ninguno {
        background-color: #040959 !important;
        border: 1.5px dashed white !important;
        color: white !important;
        font-style: italic !important;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 14px;
        font-weight: 500;
        box-shadow: none !important;
    }
    </style>    
    """, unsafe_allow_html=True)

    # === Construcción de filtros activos
    filtros_activos = []
    if categoria_pred != "Todos":
        filtros_activos.append(f"Categoría: {categoria_pred}")
    if region_pred != "Todos":
        filtros_activos.append(f"Región: {region_pred}")
    if tipo_envio != "Todas (0-30 días)":
        filtros_activos.append(f"Entrega: {tipo_envio}")

    # === Chips dinámicos con mensaje si no hay filtros activos
    if filtros_activos:
        chips_html = "<div class='chip-container'>" + "".join(
            [f"<div class='chip'>{filtro}</div>" for filtro in filtros_activos]
        ) + "</div>"
    else:
        chips_html = """
    <div class='chip-container'>
        <div class='chip chip-ninguno'>NINGÚN FILTRO SELECCIONADO</div>
    </div>
    """

    # === Render visual (título + chips integrados)
    st.markdown(f"""
    <div class="encabezado-con-filtros">
        <div style="display: flex; flex-direction: column; gap: 0.2rem; margin-bottom: 1.5rem;">
            <span style="font-size: 28px; font-weight: 900; color: black;">Predicción de Retención de Clientes</span>
        </div>
        {chips_html}
    </div>
    """, unsafe_allow_html=True)

    # === KPIs y lógica posterior
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

    # === Cálculo adicional
    num_pedidos_pred = len(df_filtrado)  

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
        <div class='kpi-box'>
            <div class='kpi-title'>Núm de Pedidos</div>
            <div class='kpi-value'>
                <span style="font-weight:900; font-size:32px;">{num_pedidos_pred:,}</span>
                <span style="font-size:18px; font-weight:600; margin-left:8px;">pedidos</span>
            </div>
            <div class='kpi-delta' style="margin-top: 6px;">
                Por todas las categorías
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # === Base sin filtrar por categoría
    df_top5 = df_proy.copy()

    # Aplicar solo los filtros de región y tipo de entrega
    if region_pred != "Todos":
        df_top5 = df_top5[df_top5['region'] == region_pred]

    if tipo_envio == "Prime (0-3 días)":
        df_top5 = df_top5[df_top5['entrega_simulada_dias'].between(0, 3)]
    elif tipo_envio == "Express (4-7 días)":
        df_top5 = df_top5[df_top5['entrega_simulada_dias'].between(4, 7)]
    elif tipo_envio == "Regular (8-30 días)":
        df_top5 = df_top5[df_top5['entrega_simulada_dias'].between(8, 30)]
    else:
        df_top5 = df_top5[df_top5['entrega_simulada_dias'].between(0, 30)]

    # Calcular top 5 categorías
    top5_pred = df_top5['categoria_de_productos'].value_counts().head(5).reset_index()
    top5_pred.columns = ['Categoría', 'Pedidos']

    # === GRÁFICA 1: Distribución
    dias = df_filtrado['entrega_simulada_dias'].dropna()
    conteo_dias = dias.value_counts().sort_index()
    conteo_dias = pd.Series(index=rango_dias, dtype=int).fillna(0).add(conteo_dias, fill_value=0).astype(int)

    # === GRÁFICA TIPO LOLLIPOP: Distribución de Entregas
    fig1 = go.Figure()

    # Líneas verticales desde 0 hasta cada valor
    for x, y in zip(conteo_dias.index, conteo_dias.values):
        fig1.add_trace(go.Scatter(
            x=[x, x],
            y=[0, y],
            mode="lines",
            line=dict(color="#497ae9", width=2),
            showlegend=False,
            hoverinfo="skip"
        ))

    # Puntos arriba de cada línea
    fig1.add_trace(go.Scatter(
        x=conteo_dias.index,
        y=conteo_dias.values,
        mode="markers",
        marker=dict(color="#7fb3ff", size=8, line=dict(width=1, color='#7fb3ff')),
        hovertemplate="Día %{x}<br>Cantidad: %{y}<extra></extra>",
        showlegend=False
    ))

    # Estilo general del layout
    fig1.update_layout(
        height=250,
        width=1250,
        title=dict(text=None, x=0.5, xanchor="center", font=dict(size=18)),
        xaxis_title="Días de Entrega",
        yaxis_title="Cantidad de Entregas",
        template="simple_white",
        margin=dict(t=10, b=100, l=10, r=30),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        font=dict(family="Arial", size=13)
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

    # Aplicar lógica: solo mostrar el tipo seleccionado si no es 'Todas'
    if tipo_envio != "Todas (0-30 días)":
        tipo_unico = tipo_envio.split(" ")[0]  # Extrae 'Prime', 'Express' o 'Regular'
        df_plot = df_plot[df_plot['tipo_entrega'] == tipo_unico]


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
            "Prime": "#19FF19",     
            "Express": "#fa73db",   
            "Regular": "#3cfdf9"    
        }
    )

    fig2.update_traces(marker=dict(size=7, line=dict(width=0.5, color='black')))

    fig2.update_layout(
        height=330,
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

    fig_top5_pred = px.bar(
        top5_pred,
        x='Categoría',
        y='Pedidos',
        color='Categoría',
        color_discrete_sequence=["#5c8aef"] * len(top5_pred)
    )

    fig_top5_pred.update_traces(
        marker_line=dict(color='#5c8aef', width=1.5),
        hovertemplate='<b>%{x}</b><br>Pedidos: %{y}<extra></extra>'
    )

    fig_top5_pred.update_layout(
        title=None,
        xaxis_title="Categoría",
        yaxis_title="Pedidos",
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        height=300,
        width=650,
        margin=dict(t=40, b=80, l=80, r=40),
        xaxis=dict(tickangle=-20, tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=12)),
        font=dict(family="Arial", size=13),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial")
    )

    html_fig3 = fig_top5_pred.to_html(full_html=False, include_plotlyjs='cdn')

    components.html(f"""
    <div style="
        box-shadow: 0px 12px 30px rgba(0, 0, 0, 0.4);
        border-radius: 16px;
        padding: 20px 20px 10px 20px;
        background-color: white;
        width: 100%;
        max-width: 1300px;
        margin: auto;
        display: flex;
        flex-direction: column;
        gap: 25px;
    ">

    <!-- FILA SUPERIOR: Top Categorías y Volumen vs Costo de Flete -->
    <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 30px;">

        <!-- GRÁFICA: Top Categorías -->
        <div style="flex: 1; max-width: 48%;">
            <div style="
                font-size: 18px;
                font-weight: 600;
                text-align: center;
                color: black;
                margin-bottom: 10px;
                font-family: Arial, sans-serif;
            ">Top Categorías</div>
            {html_fig3}
        </div>

        <!-- GRÁFICA: Volumen vs Costo de Flete -->
        <div style="flex: 1; max-width: 48%;">
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

    <!-- FILA INFERIOR: Distribución de Entregas centrada -->
    <div style="width: 100%; text-align: center;">
        <div style="
            font-size: 18px;
            font-weight: 600;
            color: black;
            margin-bottom: -2px;
            font-family: Arial, sans-serif;
        ">Distribución de Entregas</div>
        {html_fig1}
    </div>

</div>
""", height=760, scrolling=False)