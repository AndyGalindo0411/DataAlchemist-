# ================================
#           BACKEND
# ================================

import pandas as pd  # type: ignore
from pathlib import Path
import numpy as np  # type: ignore
import plotly.express as px # type: ignore
import streamlit as st # type: ignore


def mostrar_scatter_entregas_rapidas(df_estado):
    df_estado['volumen'] = pd.to_numeric(df_estado['volumen'], errors='coerce')
    df_estado['tiempo_total_entrega_dias'] = pd.to_numeric(df_estado['tiempo_total_entrega_dias'], errors='coerce')

    umbral_volumen = df_estado['volumen'].quantile(0.75)
    alto_volumen = df_estado[df_estado['volumen'] > umbral_volumen]

    alto_volumen = alto_volumen.dropna(subset=["tiempo_total_entrega_dias"])
    alto_volumen["entrega_rapida"] = alto_volumen["tiempo_total_entrega_dias"] <= 7

    fig = px.scatter(
        alto_volumen.reset_index(),
        x=alto_volumen.reset_index().index,
        y="tiempo_total_entrega_dias",
        color="entrega_rapida",
        color_discrete_map={True: "green", False: "red"},
        labels={"entrega_rapida": "¿Rápida?", "tiempo_total_entrega_dias": "Días de Entrega"},
        title="Tiempo de Entrega en Pedidos de Alto Volumen"
    )

    fig.update_layout(showlegend=True)
    st.plotly_chart(fig, use_container_width=True)


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


def aplicar_filtros(df, categoria, estado):
    df_filtrado = df if categoria == 'Todos' else df[df['categoria_nombre_producto'] == categoria]
    df_estado = df_filtrado if estado == 'Todos' else df_filtrado[df_filtrado['estado_del_cliente'] == estado]
    return df_filtrado, df_estado


def calcular_kpis(df, df_filtrado, df_estado, tipo_entrega, categoria_seleccionada, estado_seleccionado):
    df_estado['volumen'] = pd.to_numeric(df_estado['volumen'], errors='coerce')
    df_estado['tiempo_total_entrega_dias'] = pd.to_numeric(df_estado['tiempo_total_entrega_dias'], errors='coerce')

    umbral_volumen_alto = df_estado['volumen'].quantile(0.75)
    pedidos_alto_volumen = df_estado[df_estado['volumen'] > umbral_volumen_alto]
    entregas_rapidas_vol = pedidos_alto_volumen[pedidos_alto_volumen['tiempo_total_entrega_dias'] <= 7]

    porcentaje_rapidas = (
        len(entregas_rapidas_vol) / len(pedidos_alto_volumen) * 100
        if len(pedidos_alto_volumen) > 0 else 0
    )

    periodos_cat = df_filtrado.groupby('id_único_de_cliente')['periodo'].nunique()
    retenidos_cat = periodos_cat[periodos_cat > 1].count()
    totales_cat = periodos_cat.count()
    retencion_cat = (retenidos_cat / totales_cat) * 100 if totales_cat > 0 else 0
    no_retenidos_cat = 100 - retencion_cat

    dias = df_filtrado['tiempo_total_entrega_dias'].dropna()
    if tipo_entrega == "Prime (0–3 días)":
        dias_filtrados = dias[dias.between(0, 3)]
        titulo_kpi = "Entrega Promedio Prime (días)"
        rango = range(0, 4)
    elif tipo_entrega == "Express (4–7 días)":
        dias_filtrados = dias[dias.between(4, 7)]
        titulo_kpi = "Entrega Promedio Express (días)"
        rango = range(4, 8)
    elif tipo_entrega == "Regular (8–30 días)":
        dias_filtrados = dias[dias.between(8, 30)]
        titulo_kpi = "Entrega Promedio Regular (días)"
        rango = range(8, 31)
    else:
        dias_filtrados = dias[dias.between(0, 30)]
        titulo_kpi = "Entrega Promedio (días)"
        rango = range(0, 31)

    promedio_filtrado = round(dias_filtrados.mean()) if not dias_filtrados.empty else 0

    top5 = df_estado['categoria_nombre_producto'].value_counts().head(5)
    top_categoria = top5.index[0] if not top5.empty else "—"
    ventas_top = int(top5.iloc[0]) if not top5.empty else 0

    ahorro_prime = ahorro_express = None
    if 'valor_total' in df_estado.columns and 'tiempo_total_entrega_dias' in df_estado.columns:
        df_estado['valor_total'] = pd.to_numeric(df_estado['valor_total'], errors='coerce')
        df_estado['tipo_entrega'] = pd.cut(
            df_estado['tiempo_total_entrega_dias'],
            bins=[-1, 3, 7, float('inf')],
            labels=["Prime", "Express", "Regular"]
        )

        valor_promedio = df_estado.groupby("tipo_entrega")["valor_total"].mean()
        baseline = valor_promedio.get("Regular", None)

        if baseline and baseline > 0:
            ahorro_express = 100 * (baseline - valor_promedio.get("Express", 0)) / baseline
            ahorro_prime = 100 * (baseline - valor_promedio.get("Prime", 0)) / baseline

    return {
        "porcentaje_rapidas": porcentaje_rapidas,
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
