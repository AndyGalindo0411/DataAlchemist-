# datos.py
import pandas as pd
import streamlit as st
from pathlib import Path

# Cache para cargar los datos solo una vez, con spinner mientras se carga
@st.cache_data(show_spinner="Cargando base de datos...")
def cargar_datos():
    archivo = Path("UPDINTEGRADO_MODELO_FINAL.xlsx")
    
    # Verificar si el archivo existe en la ruta especificada
    if not archivo.exists():
        return None, "Archivo UPDINTEGRADO_MODELO_FINAL.xlsx no encontrado."
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(archivo)
        
        # Verificar que las columnas necesarias estén pSresentes
        required_columns = ['estado_del_pedido', 'tipo_de_pago', 'cuotas_de_pago', 'pago',
                            'numero_de_producto_id', 'precio', 'costo_de_flete',
                            'categoria_nombre_producto', 'frecuencia_de_compra_cliente',
                            'cantidad_productos_por_orden', 'volumen', 'categoria_de_productos',
                            'secuencia_corregida', 'region', 'tipo_entrega_clase']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, f"El archivo no contiene las columnas necesarias: {', '.join(missing_columns)}"
        
        # Transformaciones en los datos
        df['pago'] = pd.to_numeric(df['pago'], errors='coerce')
        df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
        df['costo_de_flete'] = pd.to_numeric(df['costo_de_flete'], errors='coerce')
        df['volumen'] = pd.to_numeric(df['volumen'], errors='coerce')
        
        # Mostrar vista previa de los datos
        st.write("Vista previa de los datos:")
        st.dataframe(df.head())  # Muestra las primeras filas del DataFrame
        
        # Mostrar los tipos de datos después de la limpieza
        st.write("Nombres de las variables y sus tipos de dato después de la limpieza:")
        st.write(df.dtypes)

        # Análisis adicional
        total_celdas = df.shape[0] * df.shape[1]  # Total de celdas en el DataFrame
        total_nulos = df.isnull().sum().sum()  # Total de valores nulos
        porcentaje_nulos = (total_nulos / total_celdas) * 100  # Porcentaje de nulos respecto al total de celdas

        # Mostrar estadísticas de celdas y valores nulos
        st.write(f"Total de celdas: {total_celdas}")
        st.write(f"Total de valores nulos: {total_nulos}")
        st.write(f"Porcentaje de datos nulos en todo el DataFrame: {porcentaje_nulos:.2f}%")

        # Devolver el DataFrame procesado y None si no hay errores
        return df, None
    
    except Exception as e:
        # En caso de error, devolver el mensaje de error
        return None, str(e)

# Función para la vista de exploración de datos
def vista_exploracion():
    # Cargar los datos
    df, error = cargar_datos()

    # Mostrar los resultados
    if error:
        st.error(error)
    else:
        # Realizar limpieza de datos
        columnas_a_convertir = [
            'pago', 'precio', 'costo_de_flete', 'volumen'
        ]

        # Reemplazar comas por puntos y convertir a numérico
        for columna in columnas_a_convertir:
            if columna in df.columns:
                # Verificamos si la columna es de tipo string antes de aplicar .str.replace()
                if df[columna].dtype == 'object':  # Si es un tipo 'object' (string en pandas)
                    df[columna] = df[columna].str.replace(',', '.', regex=False)  # Cambio de coma a punto
                # Convertir a numérico, manejando los errores con 'coerce'
                df[columna] = pd.to_numeric(df[columna], errors='coerce')     

        # Mostrar los tipos de datos después de la limpieza
        st.write("Nombres de las variables y sus tipos de dato después de la limpieza:")
        st.write(df.dtypes)

        # Análisis adicional
        total_celdas = df.shape[0] * df.shape[1]  # Total de celdas en el DataFrame
        total_nulos = df.isnull().sum().sum()  # Total de valores nulos
        porcentaje_nulos = (total_nulos / total_celdas) * 100  # Porcentaje de nulos respecto al total de celdas

        # Mostrar estadísticas de celdas y valores nulos
        st.write(f"Total de celdas: {total_celdas}")
        st.write(f"Total de valores nulos: {total_nulos}")
        st.write(f"Porcentaje de datos nulos en todo el DataFrame: {porcentaje_nulos:.2f}%")
