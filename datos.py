import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from pathlib import Path
from sklearn.preprocessing import StandardScaler  # type: ignore
from imblearn.combine import SMOTEENN  # type: ignore
from collections import Counter
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.neighbors import KNeighborsClassifier  # type: ignore
from sklearn.metrics import confusion_matrix, classification_report  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
import numpy as np  # type: ignore

@st.cache_data(show_spinner="Cargando base de datos...")
def cargar_datos():
    archivo = Path("UPDINTEGRADO_MODELO_FINAL.xlsx")
    if not archivo.exists():
        return None, "Archivo UPDINTEGRADO_MODELO_FINAL.xlsx no encontrado."
    try:
        df = pd.read_excel(archivo)
        return df, None
    except Exception as e:
        return None, str(e)

def vista_exploracion():
    st.title("Exploración del Modelo")

    df, error = cargar_datos()
    if error:
        st.error(error)
        return

    # === ✅ MODELO DENTRO DEL BOTÓN ===
    with st.expander("Descubre Nuestros Resultados", expanded=False):
        #st.header("Modelo KNN con SMOTE + ENN")

        columnas_a_eliminar = ['precio', 'pago', 'costo_de_flete', 'numero_de_producto_id',
                               'categoria_nombre_producto', 'tipo_de_pago', 'estado_del_pedido',
                               'secuencia_corregida', 'frecuencia_de_compra_cliente']
        df = df.drop(columns=columnas_a_eliminar)

        columnas_categoricas = df.select_dtypes(include='object').columns.tolist()
        df = pd.get_dummies(df, columns=columnas_categoricas, drop_first=True)

        df = df.astype({col: 'int' for col in df.select_dtypes(include='bool').columns})

        # Mostrar tipos de datos
        st.markdown("### Tipos de datos en el DataFrame post-procesamiento")
        tipos_df = df.dtypes.reset_index()
        tipos_df.columns = ['Columna', 'Tipo de Dato']
        st.dataframe(tipos_df, use_container_width=True)

        X = df.drop(columns=["tipo_entrega_clase"], errors='ignore')
        y = df["tipo_entrega_clase"]
        columnas_X = X.columns.tolist()

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        smote_enn = SMOTEENN(random_state=42)
        X_resampled, y_resampled = smote_enn.fit_resample(X_scaled, y)

        # Mostrar distribución
        st.markdown("### Distribución SMOTE + ENN")
        dist_df = pd.DataFrame.from_dict(Counter(y_resampled), orient='index', columns=['Cantidad'])
        dist_df.index.name = 'Clase'
        st.dataframe(dist_df, use_container_width=True)

        X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42)

        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(X_train, y_train)
        y_pred = knn.predict(X_test)

        labels = [0, 1, 2]
        target_names = ['Prime', 'Express', 'Regular']

        cm = confusion_matrix(y_test, y_pred, labels=labels)
        st.subheader("Matriz de Confusión")
        fig, ax = plt.subplots()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        st.pyplot(fig)

        st.subheader("Reporte de Clasificación")
        report_dict = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
        report_df = pd.DataFrame(report_dict).transpose().round(3)
        st.dataframe(report_df, use_container_width=True)

    # === ✅ EJEMPLO DE PREDICCIÓN FUERA DEL EXPANDER ===
    st.markdown("### 🎬 Ejemplo de Predicción de un Pedido Nuevo")
    volumen_demo = st.slider("Volumen del pedido", min_value=1000, max_value=100000, value=5000, step=500)
    cantidad_productos_demo = st.slider("Cantidad de productos por orden", min_value=1, max_value=10, value=1)

    region_demo = st.selectbox("Región", options=['Centro', 'Norte', 'Sur'])
    categoria_demo = st.selectbox("Categoría de producto", options=['cool_stuff', 'mascotas', 'mobiliario', 'perfumeria', 'ferramentas_jardim'])

    # Utiliza las columnas_X ya obtenidas del modelo
    if 'columnas_X' not in locals():
        st.warning("⚠️ Primero ejecuta el modelo desde el botón superior.")
        return

    valores_demo = {col: 0 for col in columnas_X}
    valores_demo['volumen'] = volumen_demo
    valores_demo['cantidad_productos_por_orden'] = cantidad_productos_demo

    if 'region_Norte' in columnas_X and region_demo == 'Norte':
        valores_demo['region_Norte'] = 1
    if 'region_Sur' in columnas_X and region_demo == 'Sur':
        valores_demo['region_Sur'] = 1

    if 'categoria_nombre_producto_mascotas' in columnas_X and categoria_demo == 'mascotas':
        valores_demo['categoria_nombre_producto_mascotas'] = 1
    if 'categoria_nombre_producto_mobiliario' in columnas_X and categoria_demo == 'mobiliario':
        valores_demo['categoria_nombre_producto_mobiliario'] = 1
    if 'categoria_nombre_producto_perfumeria' in columnas_X and categoria_demo == 'perfumeria':
        valores_demo['categoria_nombre_producto_perfumeria'] = 1
    if 'categoria_nombre_producto_ferramentas_jardim' in columnas_X and categoria_demo == 'ferramentas_jardim':
        valores_demo['categoria_nombre_producto_ferramentas_jardim'] = 1

    X_demo_df = pd.DataFrame([valores_demo])
    X_demo_scaled = scaler.transform(X_demo_df)
    y_demo_pred = knn.predict(X_demo_scaled)[0]
    pred_label = {0: 'Prime', 1: 'Express', 2: 'Regular'}

    st.success(f"👉 El modelo predice que este pedido será entregado como: **{pred_label[y_demo_pred]}** 🚚")
