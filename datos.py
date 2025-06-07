# datos.py
import streamlit as st
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from imblearn.combine import SMOTEENN
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ---------------------------
# Cargar datos
# ---------------------------
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

# ---------------------------
# Vista completa: Exploración + Modelo KNN (igual que Colab)
# ---------------------------
def vista_exploracion():
    st.title("Exploración de Datos + Modelo KNN")

    df, error = cargar_datos()
    if error:
        st.error(error)
        return

    # MODELO KNN
    st.header("Modelo KNN con SMOTE + ENN")

    # Lista de columnas a eliminar
    columnas_a_eliminar = ['precio','pago','costo_de_flete','numero_de_producto_id',
                           'categoria_nombre_producto','tipo_de_pago','estado_del_pedido',
                           'secuencia_corregida','frecuencia_de_compra_cliente']
    df = df.drop(columns=columnas_a_eliminar)

    # One-hot encoding
    columnas_categoricas = df.select_dtypes(include='object').columns.tolist()
    df = pd.get_dummies(df, columns=columnas_categoricas, drop_first=True)

    # Convertir columnas tipo bool a int
    df = df.astype({col: 'int' for col in df.select_dtypes(include='bool').columns})

    # Cantidad de tipos de datos en el df
    st.write("Tipos de datos en el DataFrame post-procesamiento:")
    st.write(df.dtypes.value_counts())

    # Paso 1: Separar X e y
    X = df.drop(columns=["tipo_entrega_clase"], errors='ignore')
    y = df["tipo_entrega_clase"]

    # Guardar columnas de X (para la demo)
    columnas_X = X.columns.tolist()

    # Paso 2: Escalar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Paso 3: Aplicar SMOTE + ENN
    smote_enn = SMOTEENN(random_state=42)
    X_resampled, y_resampled = smote_enn.fit_resample(X_scaled, y)
    st.write("Distribución SMOTE+ENN:", Counter(y_resampled))

    # Paso 4: Entrenar modelo KNN
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42)

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)

    # Etiquetas para matriz y reporte
    labels = [0, 1, 2]
    target_names = ['Prime', 'Express', 'Regular']

    # Matriz de confusión visual con heatmap
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    st.subheader("Matriz de Confusión")
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    st.pyplot(fig)

    # Reporte de clasificación
    st.subheader("Reporte de Clasificación")
    st.text(classification_report(y_test, y_pred, target_names=target_names))

    # --- DEMO VISUAL DE PREDICCIÓN ---
    st.markdown("""
    ### 🎬 Ejemplo de Predicción de un Pedido Nuevo

    A continuación, simulemos cómo el modelo predeciría el tipo de entrega para un pedido nuevo con ciertas características.
    """)

    # Slider para seleccionar valores de ejemplo
    volumen_demo = st.slider("Volumen del pedido", min_value=1000, max_value=100000, value=5000, step=500)
    cantidad_productos_demo = st.slider("Cantidad de productos por orden", min_value=1, max_value=10, value=1)

    # Región y categoría en formato one-hot
    region_demo = st.selectbox("Región", options=['Centro', 'Norte', 'Sur'])
    categoria_demo = st.selectbox("Categoría de producto", options=['cool_stuff', 'mascotas', 'mobiliario', 'perfumeria', 'ferramentas_jardim'])

    # --- Construcción del X_demo con las mismas columnas que X ---
    # Inicializar dict con todas las columnas en 0
    valores_demo = {col: 0 for col in columnas_X}

    # Asignar valores seleccionados
    valores_demo['volumen'] = volumen_demo
    valores_demo['cantidad_productos_por_orden'] = cantidad_productos_demo

    # Región
    if 'region_Norte' in columnas_X and region_demo == 'Norte':
        valores_demo['region_Norte'] = 1
    if 'region_Sur' in columnas_X and region_demo == 'Sur':
        valores_demo['region_Sur'] = 1
    # Centro queda con 0 (por drop_first=True)

    # Categoría
    if 'categoria_nombre_producto_mascotas' in columnas_X and categoria_demo == 'mascotas':
        valores_demo['categoria_nombre_producto_mascotas'] = 1
    if 'categoria_nombre_producto_mobiliario' in columnas_X and categoria_demo == 'mobiliario':
        valores_demo['categoria_nombre_producto_mobiliario'] = 1
    if 'categoria_nombre_producto_perfumeria' in columnas_X and categoria_demo == 'perfumeria':
        valores_demo['categoria_nombre_producto_perfumeria'] = 1
    if 'categoria_nombre_producto_ferramentas_jardim' in columnas_X and categoria_demo == 'ferramentas_jardim':
        valores_demo['categoria_nombre_producto_ferramentas_jardim'] = 1
    # cool_stuff queda con 0 (por drop_first=True)

    # Convertir a DataFrame
    X_demo_df = pd.DataFrame([valores_demo])

    # Escalar
    X_demo_scaled = scaler.transform(X_demo_df)

    # Predicción
    y_demo_pred = knn.predict(X_demo_scaled)[0]

    # Interpretar el resultado
    pred_label = {0: 'Prime', 1: 'Express', 2: 'Regular'}
    st.success(f"👉 El modelo predice que este pedido será entregado como: **{pred_label[y_demo_pred]}** 🚚")
