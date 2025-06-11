import streamlit as st   # type: ignore
import pandas as pd   # type: ignore
from pathlib import Path
from sklearn.preprocessing import StandardScaler   # type: ignore
from imblearn.combine import SMOTEENN   # type: ignore
from collections import Counter
from sklearn.model_selection import train_test_split   # type: ignore
from sklearn.neighbors import KNeighborsClassifier   # type: ignore
from sklearn.metrics import confusion_matrix, classification_report   # type: ignore
import matplotlib.pyplot as plt   # type: ignore
import seaborn as sns   # type: ignore
import numpy as np  # type: ignore
import plotly.express as px # type: ignore

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

@st.cache_resource
def pipeline_entrenar_knn(df_original, n_neighbors=5):
    columnas_a_eliminar = ['precio', 'pago', 'costo_de_flete', 'numero_de_producto_id',
                           'categoria_nombre_producto', 'tipo_de_pago', 'estado_del_pedido',
                           'secuencia_corregida', 'frecuencia_de_compra_cliente']
    df = df_original.drop(columns=columnas_a_eliminar)

    columnas_categoricas = df.select_dtypes(include='object').columns.tolist()
    df = pd.get_dummies(df, columns=columnas_categoricas, drop_first=True)
    df = df.astype({col: 'int' for col in df.select_dtypes(include='bool').columns})

    X = df.drop(columns=["tipo_entrega_clase"], errors='ignore')
    y = df["tipo_entrega_clase"]
    columnas_X = X.columns.tolist()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    smote_enn = SMOTEENN(random_state=42)
    X_resampled, y_resampled = smote_enn.fit_resample(X_scaled, y)

    dist_df = pd.DataFrame.from_dict(Counter(y_resampled), orient='index', columns=['Cantidad'])
    dist_df.index.name = 'Clase'

    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.3, random_state=42)

    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)

    return knn, scaler, columnas_X, y_test, y_pred, dist_df, df  

def vista_exploracion():
    st.title("Exploración del Modelo")

    df, error = cargar_datos()
    if error:
        st.error(error)
        return

    # Inicializar variable de sesión
    if 'df_predicho' not in st.session_state:
        st.session_state.df_predicho = None

    # MODELO KNN DENTRO DEL BOTÓN 
    with st.expander("Descubre Nuestros Resultados", expanded=False):

        # Llamada al pipeline cacheado
        knn, scaler, columnas_X, y_test, y_pred, dist_df, df_post = pipeline_entrenar_knn(df)

        st.markdown("### Tipos de datos en el DataFrame post-procesamiento")
        tipos_df = df_post.dtypes.reset_index()
        tipos_df.columns = ['Columna', 'Tipo de Dato']
        st.dataframe(tipos_df, use_container_width=True)

        st.markdown("### Distribución SMOTE + ENN")
        st.dataframe(dist_df, use_container_width=True)

        # Matriz de Confusión
        labels = [0, 1, 2]
        target_names = ['Prime', 'Express', 'Regular']

        cm = confusion_matrix(y_test, y_pred, labels=labels)
        st.subheader("Matriz de Confusión")
        fig, ax = plt.subplots()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        st.pyplot(fig)

        # Reporte de Clasificación
        st.subheader("Reporte de Clasificación")
        report_dict = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
        report_df = pd.DataFrame(report_dict).transpose().round(2)
        st.dataframe(report_df, use_container_width=True)

        # Guardar en sesión
        st.session_state.knn_model = knn
        st.session_state.scaler = scaler
        st.session_state.columnas_X = columnas_X

    #  PREDICCIÓN POR ARCHIVO SUBIDO EN EXPANDER
    st.markdown("---")
    with st.expander("Prueba Nuestro Modelo", expanded=False):

        archivo_subido = st.file_uploader("Sube tu archivo con pedidos (volumen, region, categoria_de_productos)", type=["csv", "xlsx"])

        if archivo_subido is not None:
            try:
                if archivo_subido.name.endswith(".csv"):
                    df_input = pd.read_csv(archivo_subido)
                else:
                    df_input = pd.read_excel(archivo_subido)

                columnas_esperadas = {'volumen', 'region', 'categoria_de_productos'}
                if not columnas_esperadas.issubset(df_input.columns):
                    st.error("El archivo debe contener las columnas: 'volumen', 'region' y 'categoria_de_productos'")
                else:
                    df_pred = df_input[['volumen', 'region', 'categoria_de_productos']].copy()
                    df_pred.columns = ['volumen', 'region', 'categoria_nombre_producto']
                    df_pred = pd.get_dummies(df_pred, drop_first=True)

                    for col in st.session_state.columnas_X:
                        if col not in df_pred.columns:
                            df_pred[col] = 0
                    df_pred = df_pred[st.session_state.columnas_X]

                    X_pred_scaled = st.session_state.scaler.transform(df_pred)
                    predicciones = st.session_state.knn_model.predict(X_pred_scaled)
                    pred_label = {0: 'Prime', 1: 'Express', 2: 'Regular'}
                    df_input['Predicción'] = [pred_label[p] for p in predicciones]

                    st.success("Predicciones Generadas")
                    st.dataframe(df_input, use_container_width=True)

                    st.session_state.df_predicho = df_input

            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

    
    # === GRÁFICA DESPUÉS DEL BOTÓN DE PREDICCIÓN ===
    if st.session_state.get("df_predicho") is not None:
        st.markdown("### Distribución de Predicciones")

        df_plot = st.session_state.df_predicho.copy()

        # Obtener regiones únicas
        regiones = sorted(df_plot['region'].dropna().unique().tolist())
        opciones = ['Todas'] + regiones

        # === Estilo CSS de los radio buttons como en tu imagen ===
        st.markdown("""
        <style>
        /* Cambia la dirección de los botones de radio a columna (uno debajo del otro) */
        div.row-widget.stRadio > div {
            flex-direction: column;
        }

        /* Estilo del título de los botones de radio ("Filtra por región") */
        div.stRadio > label {
            font-weight: 600;        /* Negrita */
            font-size: 12px;         /* Tamaño de fuente */
            margin-bottom: 8px;      /* Espacio inferior */
        }

        /* Estilo base de cada opción del radio (cuando NO está seleccionada) */
        div.stRadio > div > label {
            background-color: #f8f9fa;       /* Fondo gris claro */       /* Borde gris claro */
            padding: 6px 12px;               /* Espaciado interior (vertical y horizontal) */
            border-radius: 30px;             /* Bordes redondeados tipo "pastilla" */
            margin-bottom: 8px;              /* Espacio entre botones */
            display: flex;                   /* Contenido en línea flexible */
            align-items: center;            /* Centrado vertical */
            gap: 10px;                       /* Espacio entre el círculo y el texto */
            cursor: pointer;                /* Cambia el cursor a mano al pasar el mouse */
            transition: all 0.2s ease-in-out; /* Suaviza la animación al pasar el mouse */
        }

        /* Efecto hover (cuando el mouse está sobre el botón) */
        div.stRadio > div > label:hover {
            background-color: #c8e7f9;       /* Fondo un poco más oscuro al hacer hover */
        }

        /* Estilo cuando una opción está seleccionada */
        div.stRadio > div > label[data-selected="true"] {
            background-color: #ff4b4b !important; /* Fondo rojo intenso al seleccionar */
            color: white !important;              /* Texto blanco */
            border-color: #ff4b4b !important;     /* Borde rojo igual al fondo */
        }
        </style>
        """, unsafe_allow_html=True)

        region_seleccionada = st.radio("Filtra por región", opciones, index=0)

        if region_seleccionada != 'Todas':
            df_plot = df_plot[df_plot['region'] == region_seleccionada]

        # Graficar
        try:
            fig = px.histogram(
                df_plot,
                x="categoria_de_productos",
                color="Predicción",
                barmode="group",
                title=f"Distribución de Predicciones por Categoría {'(todas las regiones)' if region_seleccionada == 'Todas' else f'en {region_seleccionada}'}",
                labels={"categoria_de_productos": "Categoría", "Predicción": "Tipo de Entrega"},
                color_discrete_map={
                    "Prime": "#020873",    
                    "Express": "#364d99",  
                    "Regular": "#619ec5"   
                }
            )
            fig.update_layout(
                xaxis_title="Categoría de Productos",
                yaxis_title="Cantidad de Predicciones",
                legend_title="Tipo de Entrega"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo generar la gráfica: {e}")
