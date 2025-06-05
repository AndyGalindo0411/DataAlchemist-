import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go

@st.cache_data(show_spinner="Cargando base de proyección...")
def cargar_base_proyeccion():
    archivo = Path("baseProyeccion.xlsx")
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

    # === Retención proyectada y actual ===
    retenidos_proy, total_proy, retencion_proy = calcular_retencion(df_proy)
    retencion_actual = 2.95
    total_act = total_proy
    retenidos_act = int((retencion_actual / 100) * total_act)
    delta_ret = retencion_proy - retencion_actual

    # === Entrega promedio proyectada y actual ===
    entrega_actual = 11
    promedio_entrega = round(df_proy['tiempo_total_entrega_dias'].dropna().mean())
    delta_entrega = entrega_actual - promedio_entrega

    # === Tarjetas KPI estilizadas ===
    st.markdown("""
    <style>
    .kpi-box {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        width: 100%;
        text-align: center;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
        margin-bottom: 1.5rem;
    }
    .kpi-title {
        font-size: 18px;
        font-weight: 600;
        color: #333;
    }
    .kpi-value {
        font-size: 48px;
        font-weight: 900;
        color: black;
    }
    .kpi-subtext {
        font-size: 16px;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    .green { color: green; }
    .red { color: red; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Retención Actual</div>
            <div class="kpi-value">{retencion_actual:.2f} %</div>
            <div class="kpi-subtext">Clientes retenidos: {retenidos_act} de {total_act}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        color_ret = "green" if delta_ret > 0 else "red"
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Retención Proyectada</div>
            <div class="kpi-value">{retencion_proy:.2f} %</div>
            <div class="kpi-subtext {color_ret}">
                Mejora: {delta_ret:.2f} puntos<br>
                Clientes retenidos: {retenidos_proy} de {total_proy}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # === GRÁFICO DE COMPARACIÓN DE RETENCIÓN ===
    fig = go.Figure(data=[
        go.Bar(name='Actual', x=["Clientes Retenidos"], y=[retencion_actual], marker_color='#C0392B'),
        go.Bar(name='Proyección', x=["Clientes Retenidos"], y=[retencion_proy], marker_color='#27AE60')
    ])
    fig.update_layout(
        title="Comparación de Retención Actual vs Proyectada",
        yaxis_title="Porcentaje de Retención (%)",
        barmode='group',
        height=400,
        xaxis_title=None
    )
    st.plotly_chart(fig)
