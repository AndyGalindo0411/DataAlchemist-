import pandas as pd  # type: ignore
from pathlib import Path
import numpy as np  # type: ignore
import plotly.express as px  # type: ignore
import streamlit as st  # type: ignore
import plotly.graph_objects as go  # type: ignore

def mostrar_scatter_entregas_rapidas(df_estado):
    # === Limpieza ===
    df_estado['volumen'] = pd.to_numeric(df_estado['volumen'], errors='coerce')
    df_estado['tiempo_total_entrega_dias'] = pd.to_numeric(df_estado['tiempo_total_entrega_dias'], errors='coerce')
    df_estado = df_estado.dropna(subset=["volumen", "tiempo_total_entrega_dias"])

    # === Filtro ≤ 30 días ===
    df_estado = df_estado[df_estado['tiempo_total_entrega_dias'] <= 30]

    # === Solo pedidos de alto volumen ===
    umbral_volumen = df_estado['volumen'].quantile(0.75)
    alto_volumen = df_estado[df_estado['volumen'] > umbral_volumen]

    # === Bins personalizados (más claros) ===
    alto_volumen['volumen_bin'] = pd.cut(alto_volumen['volumen'], bins=6)
    alto_volumen['dias_bin'] = pd.cut(alto_volumen['tiempo_total_entrega_dias'], bins=6, right=True)

    # === Etiquetas legibles ===
    alto_volumen['volumen_str'] = alto_volumen['volumen_bin'].apply(lambda x: f"{int(x.left):,} – {int(x.right):,}")
    alto_volumen['dias_str'] = alto_volumen['dias_bin'].apply(lambda x: f"{int(x.left)} – {int(x.right)} días")

    # === Agrupación ===
    heatmap_df = alto_volumen.groupby(['volumen_str', 'dias_str']).size().reset_index(name='conteo')
    pivot_table = heatmap_df.pivot(index='volumen_str', columns='dias_str', values='conteo').fillna(0)

    # === Heatmap con color personalizado azul ===
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=list(pivot_table.columns),
        y=list(pivot_table.index),
        colorscale=[
            [0.0, "#8287DB"],
            [0.25, "#6468B3"],
            [0.5, "#424688"],
            [0.75, "#020873"],
            [1.0, '#010440']
        ],
        colorbar=dict(title='Cantidad de Pedidos'),
        hovertemplate=
            'Volumen: %{y}<br>' +
            'Días de Entrega: %{x}<br>' +
            'Cantidad: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title="Mapa de Calor: Entregas ≤ 30 días en Alto Volumen",
        xaxis=dict(
            title="Días de Entrega (0–30 días)",
            tickfont=dict(size=11, color="black"),
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title="Volumen del Pedido (rangos)",
            tickfont=dict(size=11, color="black"),
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        height=450,
        margin=dict(t=60, b=60, l=80, r=40),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

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

# === NUEVA GRÁFICA PICTOGRAMA DE RETENCIÓN ===
def grafica_barra_horizontal_retencion(retencion_cat, no_retenidos_cat):
    fig = go.Figure(go.Bar(
        x=[retencion_cat, no_retenidos_cat],
        y=["Retenidos", "No Retenidos"],
        orientation='h',
        marker=dict(color=["#27AE60", "#C0392B"]),
        text=[f"{retencion_cat:.1f}%", f"{no_retenidos_cat:.1f}%"],
        textposition='inside',
        insidetextfont=dict(size=13)  # ⬅️ texto más pequeño
    ))

    fig.update_layout(
        title=dict(
            text="Clientes Retenidos vs No Retenidos",
            x=0.5,
            xanchor="center",
            font=dict(
                size=18,
                family="Arial",
                color="black"
            )
        ),
        xaxis=dict(
            range=[0, 100],
            title=dict(
                text="Porcentaje",
                font=dict(size=13, family="Arial", color="black")
            ),
            tickfont=dict(size=12, family="Arial")
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=12, family="Arial")
        ),
        margin=dict(l=80, r=60, t=60, b=40),
        height=300,
        width=620,  # ✅ Ancho ajustado
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    return fig
