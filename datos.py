import streamlit as st # type: ignore
import pandas as pd # type: ignore

def vista_exploracion():
    st.header("Exploración de Datos")
    file = st.file_uploader("Carga un archivo Excel (.xlsx) o CSV", type=["xlsx", "csv"])
    if file:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                st.error("HOLAAAAAAAAAAAAA")
                return
            st.dataframe(df.head())
            st.success("Archivo cargado correctamente.")
        except Exception as e:
            st.error(f"Ocurrió un error al leer el archivo: {e}")
    else:
        st.info("Espera un archivo EXCEL o CSV para comenzar.")
