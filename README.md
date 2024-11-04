# 📊 Proyecto de Análisis Nutricional y Viralidad de Recetas

## Descripción del Proyecto
Este proyecto tiene como objetivo evaluar recetas culinarias en términos de su valor nutricional y su potencial viral en redes sociales. Utilizando técnicas de web scraping, APIs de nutrición y redes sociales, se analizan ingredientes y se calculan puntuaciones de salud. Esto permite no solo evaluar el contenido nutricional de las recetas, sino también explorar factores que contribuyen a su popularidad.

## Estructura del Proyecto
```
├── datos/                                  # Archivos CSV y datos en crudo
│   ├── chicken.csv                         # Recetas extraídas de YT (pollo)
│   ├── chinese.csv                         # Recetas extraídas de YT (chino)
│   ├── general.csv                         # Recetas extraídas de YT (generales)
│   ├── pasta.csv                           # Recetas extraídas de YT (pasta)
│   ├── vegan.csv                           # Recetas extraídas de YT (vegano)
│   ├── ingredientes_recetas_todas.csv      # Ingredientes de todas las recetas
├── img/                                    # Carpeta con las imágenes de las gráficas
├── notebooks/                              # Notebooks Jupyter para EDA y análisis
│   ├── 1-ETL.ipynb                         # Notebook que contiene el flujo ETL completo
│   ├── 2-EDA.ipynb                         # Notebook que contiene el EDA y las visualizaciones
├── src/                                    # Scripts de scraping, procesamiento y funciones
│   ├── query_funcs.py                      # Funciones para ejecutar queries SQL desde Python
│   ├── query_text.py                       # Texto de consultas SQL
│   ├── funcs.py                            # Funciones generales para scrapeo y procesamiento
├── environment.yml                         # Archivo de configuración para gestionar dependencias del entorno
└── README.md                               # Documentación del proyecto
```
## Instalación y Requisitos ⚙️

Para configurar el entorno de desarrollo y asegurarte de que todas las dependencias necesarias estén instaladas, sigue estos pasos:

### Requisitos

- Python 3.7 o superior 🐍
- [Anaconda](https://www.anaconda.com/products/distribution) o [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (opcional, pero recomendado)

### Paquetes Necesarios

El proyecto utiliza los siguientes paquetes:

- [`pandas`](https://pandas.pydata.org/pandas-docs/stable/): Para la manipulación y análisis de datos.
- [`numpy`](https://numpy.org/doc/stable/): Para operaciones numéricas y manejo de arrays.
- [`matplotlib`](https://matplotlib.org/stable/users/index.html): Para la visualización de datos.
- [`seaborn`](https://seaborn.pydata.org/): Para visualización estadística de datos.
- [`tqdm`](https://tqdm.github.io/): Para mostrar barras de progreso en loops.
- [`psycopg2`](https://www.psycopg.org/): Para conectar Python con PostgreSQL.
- [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): Para el scraping de datos.
- [`requests`](https://docs.python-requests.org/en/latest/): Para realizar solicitudes HTTP sencillas.
- [`selenium`](https://www.selenium.dev/): Para automatizar la navegación web.
- [`pytubefix`](https://github.com/yanruwu/pytubefix): Para buscar en YouTube.
- [`python-dotenv`](https://pypi.org/project/python-dotenv/): Para manejar variables de entorno.

### Instalación

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/yanruwu/Proyecto-Recetas
   cd Proyecto-Recetas
2. **Crea un entorno virtual:**

    Para crear el entorno de Conda, usa el siguiente comando:
    ```bash
    conda env create -f environment.yml
    ```
    O si prefieres usar venv:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En macOS/Linux
    venv\Scripts\activate     # En Windows
## Progreso del Proyecto
Este proyecto se enfoca en el desarrollo de un flujo ETL completo para analizar recetas, dividiéndose en las siguientes etapas:

### Extracción
1. **Extracción de videos de recetas de YouTube**: Usamos la librería `pytubefix`, que conecta con la API de YouTube, para obtener una lista de videos populares de recetas. Esto nos proporcionó información de títulos, descripciones y links de cada video.
2. **Búsqueda de recetas en Google**: Tras limpiar los datos obtenidos de YouTube, se utilizó un proceso de pseudo-scrapeo en Google para buscar links de páginas de recetas relevantes relacionadas con los videos, aprovechando el motor de búsqueda para identificar las URLs más asociadas a la temática de cada video.
3. **Scrapeo de sitios de recetas**: A partir de los links obtenidos en Google, se extrajo información específica de sitios como `tasty.co` y `allrecipes.com`. En estos sitios, se obtuvo el listado de ingredientes y las instrucciones de preparación, completando los datos base para el análisis.

### Transformación
1. **Limpieza y tratamiento de datos**: Los ingredientes obtenidos de los sitios web se procesaron para unificar el formato y cuantificar los nutrientes de cada uno. Se aplicaron técnicas de normalización y extracción de información clave para asegurar la coherencia de los datos nutricionales.
2. **Cálculo de puntuación de salud**: Usando los datos de nutrientes, se calculó una métrica personalizada de salud que considera proteínas, carbohidratos, grasas, fibra y azúcares. Esta métrica permite evaluar cuán saludables son las recetas y compararlas en función de sus nutrientes y su aporte calórico.

### Carga
1. **Creación e inserción en la base de datos**: Se diseñó una base de datos SQL donde se almacenaron los datos transformados de cada receta, incluyendo su valor nutricional y su puntuación de salud.

![Diagrama BBDD](img/diagrama_ddbb.png)

### EDA
1. **Análisis exploratorio**: Con la base de datos completada, se realizaron análisis de las relaciones entre la puntuación de salud de cada receta y su viralidad en redes sociales, comparando además entre tipos de recetas.
2. **Visualización de resultados**: Finalmente, se generaron visualizaciones para presentar tendencias y patrones en la popularidad de las recetas según sus características nutricionales y de tipo, brindando una visión completa de cómo lo saludable influye en la viralidad.

## Conclusiones 📈

1. **Distribución de Recetas por Tipo**: El análisis inicial reveló que las recetas más frecuentes son de tipo pasta y general, seguidas por pollo y recetas veganas, con un menor número de recetas chinas. Esta distribución nos ayuda a entender la relevancia y diversidad de las recetas en nuestro conjunto de datos, lo que influirá en los análisis posteriores.

   ![Distribución de Recetas](img\distribucion_tipos.png)

2. **Salud y Tipo de Receta 🥗**: Al analizar la puntuación de salud de las recetas según su tipo, se observó que las recetas de pollo presentan la menor dispersión en la escala de salud, lo que indica que, aunque no sean necesariamente las más saludables, tienden a ser más consistentes en su calidad nutricional. Las recetas de pasta, aunque pueden ser más saludables en algunos casos, tienen una mayor variabilidad. Las recetas generales mostraron la mayor dispersión, reflejando su diversidad inherente.

   ![Salud y Tipo de Receta](img\salud_tipo.png)

3. **Viralidad y Puntuación de Salud 📈**: El análisis de la relación entre la puntuación de salud y el número de visualizaciones reveló una clara tendencia exponencial negativa en escala logarítmica: las recetas menos saludables tienden a ser las más vistas. Esto sugiere que el contenido menos saludable puede tener un mayor atractivo entre los usuarios. Además, se identificó que las recetas generales concentran la mayor cantidad de visualizaciones, corroborando el hallazgo anterior sobre su popularidad.

   ![Viralidad y Salud](img\visitas_puntuacion.png)

4. **Tendencias de Visitas por Fecha 📅**: Al examinar las visitas en función de la fecha de publicación, se observaron picos de visualizaciones que inicialmente parecían indicar fechas de mayor viralidad. Sin embargo, estos picos estaban impulsados por las recetas generales, que tienen un volumen significativamente mayor de visitas. Al excluir estas recetas, se encontraron picos de interés a principios de año, pero se concluyó que la antigüedad de las recetas también juega un papel crucial en la acumulación de visualizaciones. El tamaño reducido del conjunto de datos sugiere que se necesita una muestra más amplia para realizar conclusiones más sólidas.

   ![Tendencias de Visitas](img\visitas_fecha.png)

5. **Ingredientes Populares 🍝**: El análisis de los ingredientes más comunes reflejó que aquellos asociados con la gastronomía italiana son predominantes, alineándose con la alta proporción de recetas de pasta en nuestro conjunto de datos. Esto indica un posible enfoque en la cocina italiana dentro de las recetas más populares, lo que podría influir en futuras recomendaciones y desarrollo de contenido.

   ![Ingredientes Populares](img\ingrediente_conteo.png)



## Próximos Pasos 🔍
1. **Precios de las recetas**: Gracias a la estructura de la BBDD el siguiente paso será usar las tablas de ingredientes para incluir los precios de éstos, para luego incluir un desglose del precio de una receta.
2. **Redes sociales**: Incluir otras fuentes de información con mayor impacto social, como podrían ser Instagram o Tiktok.
3. **Ampliar muestra**: Incluir más resultados de más recetas, lo cual permitiría sacar más y mejores conclusiones.
4. **Mejorar sistema de puntuación de salud**: Construir un sistema de puntuación más avanzado que considere otras macros y componentes de los ingredientes de cada receta.

## 🤝 Contribuciones
Las contribuciones son bienvenidas. Si deseas mejorar el proyecto, por favor abre un pull request o una issue.