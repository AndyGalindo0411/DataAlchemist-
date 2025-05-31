import matplotlib.pyplot as plt  # type: ignore
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from pathlib import Path

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

    archivo = Path("UPDINTEGRADO.xlsx")
    if not archivo.exists():
        st.warning("Archivo UPDINTEGRADO.xlsx no encontrado.")
        return

    try:
        df = pd.read_excel(archivo)
        st.session_state["df_upd"] = df

        if 'id_único_de_cliente' not in df.columns or 'orden_compra_timestamp_fecha' not in df.columns:
            st.error("El archivo no contiene las columnas necesarias.")
            return

        df['orden_compra_timestamp_fecha'] = pd.to_datetime(df['orden_compra_timestamp_fecha'])
        df['periodo'] = df['orden_compra_timestamp_fecha'].dt.to_period('M')
        df['volumen'] = pd.to_numeric(df.get('volumen', pd.Series()), errors='coerce')
        df['mes'] = df['orden_compra_timestamp_fecha'].dt.strftime('%B')

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

        df_filtrado = df if categoria_seleccionada == 'Todos' else df[df['categoria_nombre_producto'] == categoria_seleccionada]
        df_estado = df_filtrado if estado_seleccionado == 'Todos' else df_filtrado[df_filtrado['estado_del_cliente'] == estado_seleccionado]

        # === KPI 1: % Entregas Rápidas en Alto Volumen ===
        df_estado['volumen'] = pd.to_numeric(df_estado['volumen'], errors='coerce')
        df_estado['tiempo_total_entrega_dias'] = pd.to_numeric(df_estado['tiempo_total_entrega_dias'], errors='coerce')

        umbral_volumen_alto = df_estado['volumen'].quantile(0.75)
        pedidos_alto_volumen = df_estado[df_estado['volumen'] > umbral_volumen_alto]
        entregas_rapidas_vol = pedidos_alto_volumen[pedidos_alto_volumen['tiempo_total_entrega_dias'] <= 7]

        porcentaje_rapidas = (
            len(entregas_rapidas_vol) / len(pedidos_alto_volumen) * 100
            if len(pedidos_alto_volumen) > 0 else 0
        )

        # === KPI 2: Tasa de Retención ===
        df['periodo'] = df['orden_compra_timestamp_fecha'].dt.to_period('M')
        periodos_cat = df_filtrado.groupby('id_único_de_cliente')['periodo'].nunique()
        retenidos_cat = periodos_cat[periodos_cat > 1].count()
        totales_cat = periodos_cat.count()
        retencion_cat = (retenidos_cat / totales_cat) * 100 if totales_cat > 0 else 0
        no_retenidos_cat = 100 - retencion_cat

        # === KPI 3: Entrega promedio ===
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

        # === KPI 4: Top categoría ===
        top5 = df_estado['categoria_nombre_producto'].value_counts().head(5)
        top_categoria = top5.index[0] if not top5.empty else "—"
        ventas_top = int(top5.iloc[0]) if not top5.empty else 0

        # == KPI 5: Ahorro estimado por tipo de entrega ==
        kpi_html = ""
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

                kpi_html += f"""
                <div class='kpi-box'>
                    <div class='kpi-title'>Ahorro vs Regular (Express)</div>
                    <div class='kpi-value'>{ahorro_express:.2f}%</div>
                    <div class='kpi-delta up'>Entrega Express cuesta menos</div>
                </div>
                <div class='kpi-box'>
                    <div class='kpi-title'>Ahorro vs Regular (Prime)</div>
                    <div class='kpi-value'>{ahorro_prime:.2f}%</div>
                    <div class='kpi-delta up'>Entrega Prime cuesta menos</div>
                </div>
                """

        # === Mostrar KPIs ===
        st.markdown("""
        <div style='display: flex; flex-wrap: wrap; justify-content: center;'>
            <div class='kpi-box'>
                <div class='kpi-title'>% Entregas Rápidas en Alto Volumen</div>
                <div class='kpi-value'>{:.2f} %</div>
                <div class='kpi-delta'>Volumen > p75 entregado en ≤ 7 días</div>
            </div>
            <div class='kpi-box'>
                <div class='kpi-title'>Tasa de Retención ({})</div>
                <div class='kpi-value'>{:.2f} %</div>
                <div class='kpi-delta {}'>{} {:.2f}% desde 3%</div>
            </div>
            <div class='kpi-box'>
                <div class='kpi-title'>{}</div>
                <div class='kpi-value'>{}</div>
                <div class='kpi-delta'>ideal < 7 días</div>
            </div>
            <div class='kpi-box'>
                <div class='kpi-title'>Top Categoría en {}</div>
                <div class='kpi-value'>{}</div>
                <div class='kpi-delta'>{} ventas</div>
            </div>
            {}
        </div>
        """.format(
            porcentaje_rapidas,
            categoria_seleccionada,
            retencion_cat,
            "up" if retencion_cat >= 3 else "down",
            "⬆" if retencion_cat >= 3 else "⬇",
            abs(retencion_cat - 3),
            titulo_kpi,
            promedio_filtrado,
            estado_seleccionado,
            top_categoria,
            ventas_top,
            kpi_html
        ), unsafe_allow_html=True)

        # === Visualizaciones ===
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### Visualizaciones Generales")
        colv1, colv2 = st.columns(2)
        with colv1:
            st.subheader("Clientes Retenidos vs No Retenidos")
            fig_r, ax_r = plt.subplots()
            ax_r.pie([retencion_cat, no_retenidos_cat],
                     labels=["Retenidos", "No Retenidos"],
                     autopct='%1.1f%%', colors=["#55d6be", "#329fbd"], startangle=90)
            ax_r.axis('equal')
            st.pyplot(fig_r)
        with colv2:
            st.subheader("Distribución de Entregas")
            conteo_por_dia = dias_filtrados.value_counts().sort_index()
            conteo_por_dia = pd.Series(index=rango, dtype=int).fillna(0).add(conteo_por_dia, fill_value=0).astype(int)
            fig_d, ax_d = plt.subplots(figsize=(12, 4))
            ax_d.bar(conteo_por_dia.index, conteo_por_dia.values, color='#4D4FFF', edgecolor='black')
            ax_d.set_xlabel("Días de Entrega")
            ax_d.set_ylabel("Cantidad de Pedidos")
            ax_d.set_xticks(list(rango))
            ax_d.set_xlim(min(rango), max(rango))
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

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
