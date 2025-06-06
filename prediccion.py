import streamlit as st # type: ignore
import pandas as pd # type: ignore
from pathlib import Path
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore

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
