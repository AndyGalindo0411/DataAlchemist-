import matplotlib.pyplot as plt # type: ignore
import streamlit as st # type: ignore
import pandas as pd # type: ignore
from pathlib import Path

def vista_inicio():
    # === Estilos personalizados mejorados ===
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
    .kpi-box {
        background-color: #f8f9fa;
        border-radius: 12px;
        box-shadow: 0px 8px 30px rgba(0, 0, 0, 0.25);
        padding: 1.5rem 1rem 1rem 1rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .kpi-box:hover {
        transform: scale(1.02);
    }
    .kpi-title {
        font-size: 15px;
        color: #555;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 30px;
        font-weight: 800;
        color: #111;
    }
    .kpi-delta {
        font-size: 14px;
        font-weight: 500;
        margin-top: 6px;
    }
    .up {
        color: green;
    }
    .down {
        color: red;
    }
    .divider {
        margin: 2rem 0 1rem 0;
        border-top: 2px solid #d3d3d3;
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

                df["volumen"] = pd.to_numeric(df["volumen"], errors="coerce")
                df['mes'] = df['orden_compra_timestamp_fecha'].dt.strftime('%B')

                # === Filtros NUEVOS del segundo código ===
                with st.sidebar.expander("Filtros", expanded=True):
                    categorias = ['Todos'] + sorted(df['categoria_nombre_producto'].dropna().unique().tolist())
                    categoria_seleccionada = st.selectbox("Categoría", categorias)

                    tipo_entrega = st.selectbox("Tipo de Entrega", 
                                                ["De (0-30 días)", 
                                                "Prime (0–3 días)", 
                                                "Express (4–7 días)", 
                                                "Regular (8–30 días)"])

                # Filtrar por categoría
                df_filtrado = df if categoria_seleccionada == 'Todos' else df[df['categoria_nombre_producto'] == categoria_seleccionada]

                periodos_cat = df_filtrado.groupby('id_único_de_cliente')['periodo'].nunique()
                retenidos_cat = periodos_cat[periodos_cat > 1].count()
                totales_cat = periodos_cat.count()
                retencion_cat = (retenidos_cat / totales_cat) * 100 if totales_cat > 0 else 0
                no_retenidos_cat = 100 - retencion_cat

                dias = df['tiempo_total_entrega_dias'].dropna()
                if tipo_entrega == "Prime (0–3 días)":
                    dias_filtrados = dias[dias.between(0, 3)]
                    titulo = "Distribución de Entregas Prime (0–3 días)"
                    rango = range(0, 4)
                    titulo_kpi = "Entrega Promedio Prime (días)"
                elif tipo_entrega == "Express (4–7 días)":
                    dias_filtrados = dias[dias.between(4, 7)]
                    titulo = "Distribución de Entregas Express (4–7 días)"
                    rango = range(4, 8)
                    titulo_kpi = "Entrega Promedio Express (días)"
                elif tipo_entrega == "Regular (8–30 días)":
                    dias_filtrados = dias[dias.between(8, 30)]
                    titulo = "Distribución de Entregas Regular (8–30 días)"
                    rango = range(8, 31)
                    titulo_kpi = "Entrega Promedio Regular (días)"
                else:
                    dias_filtrados = dias[dias.between(0, 30)]
                    titulo = "Distribución de Entregas (0–30 días)"
                    rango = range(0, 31)
                    titulo_kpi = "Entrega Promedio (días)"

                promedio_filtrado = round(dias_filtrados.mean()) if not dias_filtrados.empty else 0

                # === KPIs NUEVOS ===
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                        <div class="kpi-box">
                            <div class="kpi-title">Tasa de Retención ({categoria_seleccionada})</div>
                            <div class="kpi-value">{retencion_cat:.2f} %</div>
                            <div class="kpi-delta down">⬇ {abs(retencion_cat - 3):.2f}% desde 3%</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                        <div class="kpi-box">
                            <div class="kpi-title">{titulo_kpi}</div>
                            <div class="kpi-value">{promedio_filtrado} días</div>
                            <div class="kpi-delta {'up' if promedio_filtrado > 7 else 'down'}">
                                {'⬆' if promedio_filtrado > 7 else '⬇'} vs ideal ≤ 7
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

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
                    st.subheader(titulo)
                    conteo_por_dia = dias_filtrados.value_counts().sort_index()
                    conteo_por_dia = pd.Series(index=rango, dtype=int).fillna(0).add(conteo_por_dia, fill_value=0).astype(int)

                    fig_d, ax_d = plt.subplots(figsize=(12, 4))
                    ax_d.bar(conteo_por_dia.index, conteo_por_dia.values, color='#4D4FFF', edgecolor='black')
                    ax_d.set_xlabel("Días de Entrega")
                    ax_d.set_ylabel("Cantidad de Pedidos")
                    ax_d.set_xticks(rango)
                    ax_d.set_xlim(min(rango), max(rango))
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
