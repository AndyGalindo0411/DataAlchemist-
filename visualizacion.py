# visualizacion.py
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

def vista_visualizacion():
    st.header("Visualización de Datos")

    # Datos de ejemplo
    df = pd.DataFrame({
        'Día': [f'Día {i}' for i in range(1, 11)],
        'Ventas': np.random.randint(100, 500, size=10)
    })

    st.subheader("Gráfica de Ventas por Día")
    chart = alt.Chart(df).mark_bar().encode(
        x='Día',
        y='Ventas',
        tooltip=['Día', 'Ventas']
    ).properties(width=600)

    st.altair_chart(chart, use_container_width=True)
    st.write("Este gráfico es un ejemplo de cómo mostrar métricas clave de forma visual.")
