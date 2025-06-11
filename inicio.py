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

    # === Líneas verticales de cada punto
    for x, y in zip(conteo_por_dia.index, conteo_por_dia.values):
        fig.add_trace(go.Scatter(
            x=[x, x],
            y=[0, y],
            mode="lines",
            line=dict(color="#5399df", width=2),
            showlegend=False,
            hoverinfo="skip"
        ))

    # === Puntos (lollipop heads)
    fig.add_trace(go.Scatter(
        x=conteo_por_dia.index,
        y=conteo_por_dia.values,
        mode="markers",
        marker=dict(color="#263cbb", size=8, line=dict(width=1, color='#263cbb')),
        hovertemplate="Día %{x}<br>Cantidad: %{y}<extra></extra>",
        showlegend=False  # 👈 Esto oculta el label
    ))

    fig.update_layout(
        height=210,
        width=1330,
        margin=dict(t=30, b=80, l=60, r=30),
        template="simple_white",
        title=None,
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

    # === RETENCIÓN USANDO SOLO ALGUNOS FILTROS (df_filtrado) ===
    # === RETENCIÓN USANDO SOLO ALGUNOS FILTROS (df_filtrado) ===
    # === RETENCIÓN CONDICIONAL SEGÚN FILTROS ===
    if categoria_seleccionada == 'Todos' and region_seleccionada == 'Todos' and tipo_entrega == 'De (0-30 días)':
        df_retencion = df_filtrado
    else:
        df_retencion = df_region

    periodos_cat = df_retencion.groupby('id_único_de_cliente')['periodo'].nunique()
    retenidos_cat = periodos_cat[periodos_cat > 1].count()
    totales_cat = periodos_cat.count()
    retencion_cat = (retenidos_cat / totales_cat) * 100 if totales_cat > 0 else 0
    no_retenidos_cat = 100 - retencion_cat


    dias = df_filtrado['tiempo_total_entrega_dias'].dropna()

    if tipo_entrega == "Prime (0–3 días)":
        dias_filtrados = dias[dias.between(0, 3)]
        titulo_kpi = "Mediana de Entrega Prime"
        rango = range(0, 4)
    elif tipo_entrega == "Express (4–7 días)":
        dias_filtrados = dias[dias.between(4, 7)]
        titulo_kpi = "Mediana de Entrega Express"
        rango = range(4, 8)
    elif tipo_entrega == "Regular (8–30 días)":
        dias_filtrados = dias[dias.between(8, 30)]
        titulo_kpi = "Mediana de Entrega Regular"
        rango = range(8, 31)
    else:
        dias_filtrados = dias[dias.between(0, 30)]
        titulo_kpi = "Mediana de Entrega"
        rango = range(0, 31)

    promedio_filtrado = round(dias_filtrados.median()) if not dias_filtrados.empty else 0

    # Reemplazado KPI anterior por nuevo conteo de pedidos
    num_pedidos = len(df_region)  # Nuevo KPI que cuenta pedidos después de todos los filtros

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
        "num_pedidos": num_pedidos,  # ✅ NUEVO KPI
        "ahorro_prime": ahorro_prime,
        "ahorro_express": ahorro_express,
        "dias_filtrados": dias_filtrados,
        "rango": rango
    }

def obtener_top5_top_categorias(df, region_seleccionada, fecha_periodo, tipo_entrega):
    df_filtrado = df.copy()

    # === Aplicar filtro de fecha ===
    if fecha_periodo is not None and fecha_periodo != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['periodo'].astype(str) == fecha_periodo]

    # === Aplicar filtro de región ===
    if region_seleccionada != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['region'] == region_seleccionada]

    # === Asegurar formato numérico ===
    df_filtrado['tiempo_total_entrega_dias'] = pd.to_numeric(df_filtrado['tiempo_total_entrega_dias'], errors='coerce')

    # === Aplicar filtro de tipo de entrega ===
    if tipo_entrega == "Prime (0–3 días)":
        df_filtrado = df_filtrado[df_filtrado['tiempo_total_entrega_dias'].between(0, 3)]
    elif tipo_entrega == "Express (4–7 días)":
        df_filtrado = df_filtrado[df_filtrado['tiempo_total_entrega_dias'].between(4, 7)]
    elif tipo_entrega == "Regular (8–30 días)":
        df_filtrado = df_filtrado[df_filtrado['tiempo_total_entrega_dias'].between(8, 30)]
    else:
        df_filtrado = df_filtrado[df_filtrado['tiempo_total_entrega_dias'].between(0, 30)]

    # === Calcular top 5 categorías ===
    top5 = df_filtrado['categoria_de_productos'].value_counts().head(5).reset_index()
    top5.columns = ['Categoría', 'Ventas']
    return top5

def mostrar_dispersion_volumen_vs_flete_filtrado(df, categoria, tipo_entrega):
    # === Filtrar solo por categoría ===
    if categoria != 'Todos':
        df = df[df['categoria_de_productos'] == categoria]

    # === Asegurar formato numérico para columnas relevantes ===
    columnas_a_convertir = ['volumen', 'costo_de_flete']
    for columna in columnas_a_convertir:
        df[columna] = df[columna].astype(str).str.replace(',', '.', regex=False)
        df[columna] = pd.to_numeric(df[columna], errors='coerce')

    # === Clasificar tipo de entrega (Prime, Express, Regular) ===
    df['tiempo_total_entrega_dias'] = pd.to_numeric(df['tiempo_total_entrega_dias'], errors='coerce')
    df['tipo_entrega'] = pd.cut(
        df['tiempo_total_entrega_dias'],
        bins=[-1, 3, 7, 30],
        labels=["Prime", "Express", "Regular"]
    )

    # === Filtrar por tipo_entrega (si aplica) ===
    if tipo_entrega == "Prime (0–3 días)":
        df = df[df['tipo_entrega'] == "Prime"]
    elif tipo_entrega == "Express (4–7 días)":
        df = df[df['tipo_entrega'] == "Express"]
    elif tipo_entrega == "Regular (8–30 días)":
        df = df[df['tipo_entrega'] == "Regular"]
    else:
        df = df[df['tipo_entrega'].notna()]  # Todos los tipos válidos

    # === Limpiar NaNs ===
    df = df.dropna(subset=['volumen', 'costo_de_flete'])

    # === Crear gráfica de dispersión con color por tipo de entrega ===
    fig = px.scatter(
        df,
        x='volumen',
        y='costo_de_flete',
        color='tipo_entrega',
        color_discrete_map={
            'Prime': "#05d721",    # Azul oscuro
            'Express': "#dd0f98",  # Azul medio #41B6F0
            'Regular': "#1329ee"   # Azul claro #09479E
        },
        labels={
            'volumen': 'Volumen (cm³)',
            'costo_de_flete': 'Costo de Flete ($)',
            'tipo_entrega': 'Tipo de Entrega'
        },
        opacity=0.7
    )

    fig.update_traces(marker=dict(size=7, line=dict(width=0.5, color='black')))

    fig.update_layout(
        height=250,
        width=600,
        margin=dict(t=0, b=80, l=60, r=30),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    return fig