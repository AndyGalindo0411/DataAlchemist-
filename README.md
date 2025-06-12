# Danu Shop by Data Alchemist

Danu Shop es una aplicación interactiva desarrollada con Streamlit que permite explorar, analizar y predecir datos relacionados con la retención de clientes y la logística en un entorno de comercio electrónico. La aplicación incluye múltiples vistas para facilitar la navegación y el análisis de datos.

## Estructura del Proyecto

El proyecto está organizado en los siguientes archivos y carpetas:

### Archivos principales
- **Page1.py**: Archivo principal que configura la navegación entre las diferentes vistas de la aplicación.
- **inicioFront.py**: Vista principal del dashboard de Danu Shop, que muestra indicadores clave y gráficos interactivos.
- **datos.py**: Contiene la lógica para cargar datos, entrenar un modelo KNN y realizar predicciones.
- **prediccionFront.py**: Vista para analizar la predicción de retención de clientes basada en filtros y gráficos interactivos.
- **prediccion.py**: Funciones auxiliares para cargar datos y calcular métricas de retención.
- **introduccion.py**: Vista introductoria con citas motivacionales y explicaciones sobre la importancia de la retención de clientes.
- **conclusion.py**: Vista de conclusión que resume los hallazgos y propone estrategias para mejorar la retención.
- **configuracion.py**: Vista para configurar parámetros de la aplicación, como el tema y la frecuencia de actualización.
- **style.css**: Archivo de estilos personalizados para mejorar la apariencia de la aplicación.

### Archivos de datos
- **UPDINTEGRADO_MODELO_FINAL.xlsx**: Archivo de datos utilizado para entrenar el modelo KNN.
- **UPDINTEGRADO.xlsx**: Archivo de datos utilizado para el análisis general.
- **DATASETFINALOK.xlsx**: Archivo de datos utilizado para la predicción de retención.

### Carpetas
- **Imagenes/**: Contiene imágenes utilizadas en las vistas de introducción y conclusión.
- **.streamlit/**: Configuración de temas para la aplicación.

## Funcionalidades

### Navegación
La aplicación permite navegar entre las siguientes secciones:
1. **Inicio**: Introducción al proyecto y motivación.
2. **Danu Shop**: Dashboard interactivo con KPIs y gráficos.
3. **Exploración de Datos**: Entrenamiento de un modelo KNN y predicción basada en datos subidos por el usuario.
4. **Predicción**: Análisis de retención de clientes con filtros avanzados.
5. **Conclusión**: Resumen de hallazgos y estrategias.

### Predicción
- Entrenamiento de un modelo KNN para clasificar tipos de entrega (Prime, Express, Regular).
- Predicción basada en datos subidos por el usuario.
- Visualización de resultados en gráficos interactivos.

### Análisis
- KPIs como tasa de retención, mediana de entrega y volumen logístico.
- Gráficos de dispersión, histogramas y distribuciones de entrega.

### Configuración
- Personalización del tema (claro u oscuro).
- Ajuste de parámetros como frecuencia de actualización.

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-repositorio/data-alchemist.git
