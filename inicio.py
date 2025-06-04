import pandas as pd  # type: ignore
from pathlib import Path
import numpy as np  # type: ignore
import plotly.express as px  # type: ignore
import streamlit as st  # type: ignore
import plotly.graph_objects as go  # type: ignore

def mostrar_linea_distribucion_entregas(dias_filtrados, rango):
    conteo_por_dia = dias_filtrados.value_counts().sort_index()
    conteo_por_dia = pd.Series(index=rango, dtype=int).fillna(0).add(conteo_por_dia, fill_value=0).astype(int)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=conteo_por_dia.index,
        y=conteo_por_dia.values,
        mode="lines+markers",
        line=dict(color="#040959", width=3),
        fill='tozeroy',
        marker=dict(size=6),
        hovertemplate="Día %{x}<br>Cantidad: %{y}<extra></extra>"
    ))

    fig.update_layout(
        height=300,
        width=550,  # ⬅️ más compacto para que no se pierdan etiquetas
        margin=dict(t=30, b=80, l=60, r=30),  # ⬅️ más margen inferior para etiquetas
        template="simple_white",
        xaxis=dict(
            title="Días de Entrega",
            tickmode="linear",
            dtick=2,
            tickangle=0,
            tickfont=dict(size=11, color="black"),
            showticklabels=True
        ),
        yaxis=dict(
            title="Cantidad de Entregas",
            tickfont=dict(size=12, color="black")
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    return fig

@st.cache_data(show_spinner="Cargando base de datos...")
def cargar_datos():
    archivo = Path("UPDINTEGRADO.xlsx")
    if not archivo.exists():
        return None, "Archivo UPDINTEGRADO.xlsx no encontrado."
    try:
        df = pd.read_excel(archivo)
        if 'id_único_de_cliente' not in df.columns or 'orden_compra_timestamp_fecha' not in df.columns:
            return None, "El archivo no contiene las columnas necesarias."

        df['orden_compra_timestamp_fecha'] = pd.to_datetime(df['orden_compra_timestamp_fecha'])
        df['periodo'] = df['orden_compra_timestamp_fecha'].dt.to_period('M')
        df['volumen'] = pd.to_numeric(df.get('volumen', pd.Series()), errors='coerce')
        df['mes'] = df['orden_compra_timestamp_fecha'].dt.strftime('%B')

        return df, None
    except Exception as e:
        return None, str(e)

def aplicar_filtros(df, categoria, region, tipo_entrega, fecha_periodo):
    if fecha_periodo is not None and fecha_periodo != 'Todos':
        df = df[df['periodo'].astype(str) == fecha_periodo]

    df_filtrado = df if categoria == 'Todos' else df[df['categoria_de_productos'] == categoria]

    if 'region' in df_filtrado.columns:
        df_region = df_filtrado if region == 'Todos' else df_filtrado[df_filtrado['region'] == region]
    else:
        df_region = df_filtrado.copy()

    df_region = df_region.copy()
    df_region['tiempo_total_entrega_dias'] = pd.to_numeric(df_region['tiempo_total_entrega_dias'], errors='coerce')

    if tipo_entrega == "Prime (0–3 días)":
        df_region = df_region[df_region['tiempo_total_entrega_dias'].between(0, 3)]
    elif tipo_entrega == "Express (4–7 días)":
        df_region = df_region[df_region['tiempo_total_entrega_dias'].between(4, 7)]
    elif tipo_entrega == "Regular (8–30 días)":
        df_region = df_region[df_region['tiempo_total_entrega_dias'].between(8, 30)]
    else:
        df_region = df_region[df_region['tiempo_total_entrega_dias'].between(0, 30)]

    return df_filtrado, df_region

def calcular_kpis(df, df_filtrado, df_region, tipo_entrega, categoria_seleccionada, region_seleccionada):
    df_region['volumen'] = pd.to_numeric(df_region['volumen'], errors='coerce')
    df_region['tiempo_total_entrega_dias'] = pd.to_numeric(df_region['tiempo_total_entrega_dias'], errors='coerce')

    df_region['tipo_entrega'] = pd.cut(
        df_region['tiempo_total_entrega_dias'],
        bins=[-1, 3, 7, float('inf')],
        labels=["Prime", "Express", "Regular"]
    )

    volumen_promedio = 0
    df_categoria = df_region if categoria_seleccionada == 'Todos' else df_region[df_region['categoria_de_productos'] == categoria_seleccionada]
    tipo = tipo_entrega.split()[0] if tipo_entrega != "De (0-30 días)" else None

    if tipo:
        df_tipo = df_categoria[df_categoria['tipo_entrega'] == tipo]
        volumen_promedio = df_tipo['volumen'].mean()
    else:
        volumen_promedio = df_categoria['volumen'].mean()

    volumen_promedio = round(volumen_promedio, 2) if not pd.isna(volumen_promedio) else 0

    periodos_cat = df_filtrado.groupby('id_único_de_cliente')['periodo'].nunique()
    retenidos_cat = periodos_cat[periodos_cat > 1].count()
    totales_cat = periodos_cat.count()
    retencion_cat = (retenidos_cat / totales_cat) * 100 if totales_cat > 0 else 0
    no_retenidos_cat = 100 - retencion_cat

    dias = df_filtrado['tiempo_total_entrega_dias'].dropna()
    if tipo_entrega == "Prime (0–3 días)":
        dias_filtrados = dias[dias.between(0, 3)]
        titulo_kpi = "Volumen Promedio Prime"
        rango = range(0, 4)
    elif tipo_entrega == "Express (4–7 días)":
        dias_filtrados = dias[dias.between(4, 7)]
        titulo_kpi = "Volumen Promedio Express"
        rango = range(4, 8)
    elif tipo_entrega == "Regular (8–30 días)":
        dias_filtrados = dias[dias.between(8, 30)]
        titulo_kpi = "Volumen Promedio Regular"
        rango = range(8, 31)
    else:
        dias_filtrados = dias[dias.between(0, 30)]
        titulo_kpi = "Volumen Promedio (todos)"
        rango = range(0, 31)

    promedio_filtrado = round(dias_filtrados.mean()) if not dias_filtrados.empty else 0

    df_region_top = df if region_seleccionada == 'Todos' else df[df['region'] == region_seleccionada]
    top5_region = df_region_top['categoria_de_productos'].value_counts().head(5)
    top_categoria = top5_region.index[0] if not top5_region.empty else "—"
    ventas_top = int(top5_region.iloc[0]) if not top5_region.empty else 0

    ahorro_prime = ahorro_express = None
    if 'valor_total' in df_region.columns and 'tiempo_total_entrega_dias' in df_region.columns:
        df_region['valor_total'] = pd.to_numeric(df_region['valor_total'], errors='coerce')
        valor_promedio = df_region.groupby("tipo_entrega")["valor_total"].mean()
        baseline = valor_promedio.get("Regular", None)

        if baseline and baseline > 0:
            ahorro_express = 100 * (baseline - valor_promedio.get("Express", 0)) / baseline
            ahorro_prime = 100 * (baseline - valor_promedio.get("Prime", 0)) / baseline

    return {
        "volumen_promedio": volumen_promedio,
        "retencion_cat": retencion_cat,
        "no_retenidos_cat": no_retenidos_cat,
        "titulo_kpi": titulo_kpi,
        "promedio_filtrado": promedio_filtrado,
        "top_categoria": top_categoria,
        "ventas_top": ventas_top,
        "ahorro_prime": ahorro_prime,
        "ahorro_express": ahorro_express,
        "dias_filtrados": dias_filtrados,
        "rango": rango
    }

def obtener_top5_top_categorias(df, region_seleccionada, fecha_periodo):
    df_filtrado = df.copy()

    # Aplicar filtro de fecha si se selecciona
    if fecha_periodo is not None and fecha_periodo != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['periodo'].astype(str) == fecha_periodo]

    # Aplicar filtro de región si se selecciona
    if region_seleccionada != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['region'] == region_seleccionada]

    # Calcular top 5 categorías
    top5 = df_filtrado['categoria_de_productos'].value_counts().head(5).reset_index()
    top5.columns = ['Categoría', 'Ventas']
    return top5

def mostrar_dispersion_volumen_vs_flete_filtrado(df, categoria, tipo_entrega):
    # === Filtrar solo por categoría ===
    if categoria != 'Todos':
        df = df[df['categoria_de_productos'] == categoria]

    # === Asegurar formato numérico ===
    df['tiempo_total_entrega_dias'] = pd.to_numeric(df['tiempo_total_entrega_dias'], errors='coerce')
    df['volumen'] = pd.to_numeric(df['volumen'], errors='coerce')
    df['costo_de_flete'] = pd.to_numeric(df['costo_de_flete'], errors='coerce')

    # === Filtrar por tipo de entrega ===
    if tipo_entrega == "Prime (0–3 días)":
        df = df[df['tiempo_total_entrega_dias'].between(0, 3)]
    elif tipo_entrega == "Express (4–7 días)":
        df = df[df['tiempo_total_entrega_dias'].between(4, 7)]
    elif tipo_entrega == "Regular (8–30 días)":
        df = df[df['tiempo_total_entrega_dias'].between(8, 30)]
    else:
        df = df[df['tiempo_total_entrega_dias'].between(0, 30)]

    # === Limpiar NaNs ===
    df = df.dropna(subset=['volumen', 'costo_de_flete'])

    fig = px.scatter(
        df,
        x='volumen',
        y='costo_de_flete',
        labels={
            'volumen': 'Volumen (cm³)',
            'costo_de_flete': 'Costo de Flete ($)',
        },
        opacity=0.7
    )

    fig.update_traces(marker=dict(color='rgba(4, 9, 89, 0.7)'), showlegend=False)

    fig.update_layout(
        height=400,
        margin=dict(t=0, b=80, l=60, r=30),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
    )

    return fig
