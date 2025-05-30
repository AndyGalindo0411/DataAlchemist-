import matplotlib.pyplot as plt  # type: ignore
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from pathlib import Path

def vista_inicio():
    # === Estilos personalizados ===
    st.markdown("""
        <style>
        .block-container {
            padding-top: 3rem !important;
        }
        .titulo-principal {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 0.25rem;
        }
        .subtitulo {
            font-size: 20px;
            font-weight: 500;
            color: #444;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # === Encabezado ===
    st.markdown("<div class='titulo-principal'>Danu Shop</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitulo'>Panel de Indicadores Clave y Estratégicos</div>", unsafe_allow_html=True)

    archivo = Path("UPDINTEGRADO.xlsx")
    if archivo.exists():
        try:
            df = pd.read_excel(archivo)
            st.session_state["df_upd"] = df

            if 'id_único_de_cliente' in df.columns and 'orden_compra_timestamp_fecha' in df.columns:
                df['orden_compra_timestamp_fecha'] = pd.to_datetime(df['orden_compra_timestamp_fecha'])
                df['periodo'] = df['orden_compra_timestamp_fecha'].dt.to_period('M')

                periodos = df.groupby('id_único_de_cliente')['periodo'].nunique()
                retenidos = periodos[periodos > 1].count()
                totales = periodos.count()
                retencion = (retenidos / totales) * 100

                # === Filtros ===
                with st.sidebar.expander("Filtros", expanded=True):
                    st.markdown("**Seleccione la métrica:**")
                    metrica_sel = st.radio("", ["Unidades vendidas", "Tiempo de entrega", "Volumen de pedidos"], index=0)

                    df['mes'] = df['orden_compra_timestamp_fecha'].dt.strftime('%B')
                    meses = sorted(df['mes'].dropna().unique().tolist())
                    mes_sel = st.selectbox("Selecciona un mes", meses)

                    categorias = sorted(df["categoria_nombre_producto"].dropna().unique().tolist())
                    cat_sel = st.selectbox("Categoría del Producto", categorias)

                    estados = sorted(df["estado_del_cliente"].dropna().unique().tolist())
                    estado_sel = st.selectbox("Estado del Cliente", estados)

                    df["volumen"] = pd.to_numeric(df["volumen"], errors="coerce")
                    vol_max = df["volumen"].max()
                    vol_fil = st.slider("Filtrar volumen máximo", 0.0, float(vol_max), float(vol_max), step=10.0)

                df_cat = df[df["categoria_nombre_producto"] == cat_sel]
                df_estado = df[df["estado_del_cliente"] == estado_sel].copy()
                df_estado["fecha_entrega_al_cliente_fecha"] = pd.to_datetime(df_estado["fecha_entrega_al_cliente_fecha"])
                df_estado["fecha_de_entrega_estimada_fecha"] = pd.to_datetime(df_estado["fecha_de_entrega_estimada_fecha"])
                df_estado["retraso_dias"] = (df_estado["fecha_entrega_al_cliente_fecha"] - df_estado["fecha_de_entrega_estimada_fecha"]).dt.days
                df_vol = df[df["volumen"] <= vol_fil]

                # === KPIs sin recuadro ===
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric("Tasa de Retención", f"{retencion:.2f} %", delta=f"{retencion - 3:.2f} % desde 3%")

                with col2:
                    promedio = df['tiempo_total_entrega_dias'].dropna().mean()
                    if promedio <= 6:
                        rango = "4-6 días"
                    elif promedio <= 8:
                        rango = "6-8 días"
                    elif promedio <= 10:
                        rango = "8-10 días"
                    else:
                        rango = "+10 días"
                    st.metric("Entrega Promedio", rango)

                with col3:
                    entregas_prime = df_cat[df_cat["tiempo_total_entrega_dias"] <= 3]
                    perc_prime = (len(entregas_prime) / len(df_cat)) * 100 if len(df_cat) > 0 else 0
                    st.metric("Entregas Prime (≤3 días)", f"{perc_prime:.2f} %")

                with col4:
                    retraso_prom = df_estado["retraso_dias"].mean()
                    st.metric("Retraso Promedio", f"{retraso_prom:.2f} días")

                with col5:
                    entregas_reg = df_vol[df_vol["tiempo_total_entrega_dias"] > 7]
                    perc_reg = (len(entregas_reg) / len(df_vol)) * 100 if len(df_vol) > 0 else 0
                    st.metric("Entregas Regulares (8+ días)", f"{perc_reg:.2f} %")

                # === Visualizaciones ===
                colv1, colv2 = st.columns(2)

                with colv1:
                    st.subheader("Entregas Prime por Categoría")
                    fig1, ax1 = plt.subplots()
                    df_cat_hist = df_cat["tiempo_total_entrega_dias"]
                    ax1.hist(df_cat_hist[df_cat_hist <= 10], bins=10, color="#4D4FFF", edgecolor="black")
                    ax1.set_xlabel("Días de Entrega")
                    ax1.set_ylabel("Número de Pedidos")
                    ax1.set_title(f"Categoría: {cat_sel}")
                    st.pyplot(fig1)

                    st.subheader("Clientes Retenidos vs No Retenidos")
                    fig_r, ax_r = plt.subplots()
                    no_retenidos = 100 - retencion
                    ax_r.pie([retencion, no_retenidos], labels=["Retenidos", "No Retenidos"],
                             autopct='%1.1f%%', colors=["#55d6be", "#329fbd"], startangle=90)
                    ax_r.axis('equal')
                    st.pyplot(fig_r)

                with colv2:
                    st.subheader("Retraso Promedio por Estado")
                    fig2, ax2 = plt.subplots()
                    ax2.hist(df_estado["retraso_dias"].dropna(), bins=10, color="#FF4D4D", edgecolor="black")
                    ax2.set_xlabel("Días de Retraso")
                    ax2.set_ylabel("Número de Pedidos")
                    ax2.set_title(f"Estado: {estado_sel}")
                    st.pyplot(fig2)

                    st.subheader("Distribución de Entregas (0-30 días)")
                    dias = df['tiempo_total_entrega_dias'].dropna()
                    conteo_por_dia = dias.value_counts().sort_index()
                    rango_completo = pd.Series(index=range(0, 31), dtype=int).fillna(0)
                    conteo_por_dia = rango_completo.add(conteo_por_dia, fill_value=0).astype(int)

                    fig_d, ax_d = plt.subplots(figsize=(12, 4))
                    ax_d.bar(conteo_por_dia.index, conteo_por_dia.values, color='#4D4FFF', edgecolor='black')
                    ax_d.set_xlabel("Días de Entrega")
                    ax_d.set_ylabel("Cantidad de Pedidos")
                    ax_d.set_xticks(range(0, 31, 2))
                    ax_d.set_xlim(0, 30)
                    ax_d.grid(True, axis='y')
                    st.pyplot(fig_d)

                # === Branding lateral ===
                st.sidebar.markdown("""
                    <hr style='margin-top: 12px; margin-bottom: 4px;'>
                    <p style='font-size: 11px; text-align: center; margin: 0; color: #444;'>
                        Todos los derechos reservados<br><strong>DataAlchemist</strong>
                    </p>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
    else:
        st.warning("Archivo UPDINTEGRADO.xlsx no encontrado.")
