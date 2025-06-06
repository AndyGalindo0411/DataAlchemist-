import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

@st.cache_data(show_spinner="Cargando base de proyección...")
def cargar_base_proyeccion():
    archivo = Path("baseProyeccion_ultrapro.xlsx")
    if not archivo.exists():
        return None, "Archivo baseProyeccion.xlsx no encontrado."
    try:
        df = pd.read_excel(archivo)
        return df, None
    except Exception as e:
        return None, str(e)

def calcular_retencion(df):
    if 'retencion' not in df.columns:
        return 0, 0, 0.0
    total_clientes = len(df)
    retenidos = df['retencion'].sum()
    retencion = (retenidos / total_clientes) * 100 if total_clientes > 0 else 0
    return int(retenidos), total_clientes, retencion

def vista_prediccion():
    st.title("Predicción de Retención de Clientes")

    df_proy, error = cargar_base_proyeccion()
    if error:
        st.error(error)
        return

    tipo_envio = st.selectbox(
        "Filtrar por tipo de entrega:",
        ("Todas (0-30 días)", "Prime (0-3 días)", "Express (4-7 días)", "Regular (8-30 días)")
    )

    # === Filtro y rango dinámico ===
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

    #  KPIs 
    retenidos_proy, total_proy, retencion_proy = calcular_retencion(df_filtrado)
    retenidos_total, total_clientes_total, retencion_total = calcular_retencion(df_proy)

    # Porcentaje de clientes filtrados sobre total clientes
    total_clientes_filtrados = len(df_filtrado)
    proporcion_clientes_filtrados = (total_clientes_filtrados / total_clientes_total) * 100 if total_clientes_total > 0 else 0

    #  Definir retencion_actual dinámico según filtro 
    retencion_actual_dict = {
        "Todas (0-30 días)": 2.95,
        "Prime (0-3 días)": 0.25,
        "Express (4-7 días)": 0.73,
        "Regular (8-30 días)": 1.97
    }

    # Según el filtro actual, obtener retencion_actual
    retencion_actual = retencion_actual_dict.get(tipo_envio, 2.95)

    #  Calcular TASA correcta (global del segmento, que ya te pasé antes)
    tasa_retencion_global_segmento = (retenidos_proy / total_clientes_total) * 100 if total_clientes_total > 0 else 0

    #  Calcular delta en puntos
    delta_ret = tasa_retencion_global_segmento - retencion_actual

    entrega_actual = 10
    mediana_entrega = round(df_filtrado['entrega_simulada_dias'].dropna().median())
    delta_entrega = entrega_actual - mediana_entrega

    volumen_median = round(df_filtrado['volumen'].dropna().median(), 2)
    volumen_total_median = round(df_proy['volumen'].dropna().median(), 2)
    volumen_relativo_pct = (volumen_median / volumen_total_median) * 100 if volumen_total_median > 0 else 0

    # === Estilos visuales ===
    st.markdown("""<style>
    .kpi-box { background:#fff;border-radius:12px;padding:1.2rem;width:100%;
    text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.10);margin-bottom:1rem;}
    .kpi-title { font-size:16px;font-weight:600;color:#333; }
    .kpi-value { font-size:36px;font-weight:800;color:black; }
    .kpi-subtext { font-size:14px;margin-top:0.4rem; }
    .green { color:green; } .red { color:red; }
    </style>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # === KPI 1: Retención ===
    # Esta es la tasa que SÍ quieres mostrar: retenidos_proy sobre el total general de clientes
    tasa_retencion_global_segmento = (retenidos_proy / total_clientes_total) * 100 if total_clientes_total > 0 else 0

    with col1:
        puntos_texto = "punto" if abs(delta_ret) == 1 else "puntos"
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Tasa de Retención de Clientes</div>
            <div class="kpi-value">{tasa_retencion_global_segmento:.2f} %</div>
            <div class="kpi-subtext green">Mejora: {abs(delta_ret):.2f} {puntos_texto}</div>
        </div>
        """, unsafe_allow_html=True)

    # === KPI 2: Mediana de entrega ===
    with col2:
        color_entrega = "green" if mediana_entrega < entrega_actual else "red"
        mejora_entrega = entrega_actual - mediana_entrega
        unidad_dias = "día" if abs(mejora_entrega) == 1 else "días"
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Mediana de Entrega</div>
            <div class="kpi-value">{mediana_entrega} días</div>
            <div class="kpi-subtext {color_entrega}">
                Mejora: {abs(mejora_entrega)} {unidad_dias}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # === KPI 3: Volumen ===
    with col3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Volumen Logístico (Mediana)</div>
            <div class="kpi-value">{volumen_median:,.0f} cm³</div>
            <div class="kpi-subtext green">Distribución eficiente</div>
        </div>
        """, unsafe_allow_html=True)

    # === Gráfico 1: Distribución de entregas ===
    dias = df_filtrado['entrega_simulada_dias'].dropna()
    conteo_dias = dias.value_counts().sort_index()
    conteo_dias = pd.Series(index=rango_dias, dtype=int).fillna(0).add(conteo_dias, fill_value=0).astype(int)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=conteo_dias.index,
        y=conteo_dias.values,
        mode="lines+markers",
        fill='tozeroy',
        line=dict(color="green", width=3),
        hovertemplate="Día %{x}<br>Cantidad: %{y}<extra></extra>"
    ))
    fig1.update_layout(
        height=360,
        title="Días estimados de entrega tras mejoras logísticas",
        xaxis_title="Días de Entrega",
        yaxis_title="Cantidad de Entregas",
        template="simple_white"
    )

    # === Gráfico 2: Volumen vs Costo ===
    df_plot = df_filtrado.dropna(subset=['volumen', 'costo_de_flete'])
    fig2 = px.scatter(
        df_plot,
        x="volumen",
        y="costo_de_flete",
        opacity=0.6,
        labels={"volumen": "Volumen (cm³)", "costo_de_flete": "Costo de Flete ($)"}
    )
    fig2.update_traces(marker=dict(color="green"))
    fig2.update_layout(
        height=360,
        xaxis_title="Volumen",
        yaxis_title="Costo de Flete",
        title="Relación más eficiente entre volumen y costos"
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        st.plotly_chart(fig2, use_container_width=True)