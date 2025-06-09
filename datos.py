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

        # === ✅ PREDICCIÓN POR ARCHIVO SUBIDO ===
    st.markdown("---")
    st.markdown(" Modelo KNN ")

    archivo_subido = st.file_uploader("Sube tu archivo con pedidos (volumen, region, categoria_de_productos)", type=["csv", "xlsx"])

    if archivo_subido is not None:
        try:
            if archivo_subido.name.endswith(".csv"):
                df_input = pd.read_csv(archivo_subido)
            else:
                df_input = pd.read_excel(archivo_subido)

            # Validación mínima
            columnas_esperadas = {'volumen', 'region', 'categoria_de_productos'}
            if not columnas_esperadas.issubset(df_input.columns):
                st.error("El archivo debe contener las columnas: 'volumen', 'region' y 'categoria_de_productos'")
                return

            # Seleccionar solo columnas necesarias
            df_pred = df_input[['volumen', 'region', 'categoria_de_productos']].copy()

            # Asegurar que las columnas tienen el mismo nombre que las del modelo original
            df_pred.columns = ['volumen', 'region', 'categoria_nombre_producto']

            # Aplicar get_dummies igual que al modelo original
            df_pred = pd.get_dummies(df_pred, drop_first=True)

            # Asegurar que tenga las mismas columnas que el modelo entrenado (rellenar con 0 donde falten)
            for col in columnas_X:
                if col not in df_pred.columns:
                    df_pred[col] = 0
            df_pred = df_pred[columnas_X]  # Reordenar columnas igual que X del modelo

            # Escalar y predecir
            X_pred_scaled = scaler.transform(df_pred)
            predicciones = knn.predict(X_pred_scaled)
            pred_label = {0: 'Prime', 1: 'Express', 2: 'Regular'}
            df_input['Predicción'] = [pred_label[p] for p in predicciones]

            st.success("✅ Predicciones generadas correctamente.")
            st.dataframe(df_input)

            # ✅ Botón de descarga
            csv_out = df_input.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar archivo con predicciones", csv_out, file_name="predicciones.csv", mime="text/csv")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
