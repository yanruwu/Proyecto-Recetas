from fractions import Fraction
import re
from selenium import webdriver
import urllib.parse
from selenium.webdriver.common.by import By
import pandas as pd
from pytubefix.contrib.search import Search
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from time import sleep
import numpy as np
import os

def obtener_links(receta):
    """Busca y devuelve el enlace de la receta más relevante en sitios específicos.

    Esta función utiliza Selenium para realizar una búsqueda en Google y obtener enlaces
    a recetas desde los sitios `allrecipes.com` y `tasty.co`. Luego, selecciona el enlace
    más relevante basado en la coincidencia de palabras con el nombre de la receta proporcionada.

    Args:
        receta (str): Nombre de la receta para buscar en Google.

    Returns:
        str: URL del enlace de receta más relevante encontrado, o `None` si no se encuentra ningún enlace.

    Raises:
        selenium.common.exceptions.NoSuchElementException: Si no se encuentra algún elemento esperado.
        selenium.common.exceptions.WebDriverException: Si hay un error en la conexión con el navegador o en el controlador.
        Exception: Para otros errores generales durante la ejecución del proceso.
    """
    
    driver = webdriver.Chrome()
    query = urllib.parse.quote(f"{receta} site:allrecipes.com/recipe OR site:tasty.co/recipe")
    search_url = f"https://google.com/search?q={query}"
    # print(search_url)
    driver.get(search_url)
    try:
        element = driver.find_element(By.XPATH, "//*[text()='Rechazar todo']")
        element.click()
    except:
        pass
    try:
        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'allrecipes.com/recipe/') or contains(@href, 'tasty.co/recipe/')]")
        shared_words = 0

        for link in links:
            try: #? A veces coge la imagen de previsualización de google
                compare_name = set(link.find_element(By.TAG_NAME, 'h3').text.lower().split())
            except:
                continue
            shared_it = len(compare_name.intersection(set(receta.lower().split())))
            if shared_it > shared_words: #* Next steps: hacer que coja también la que tenga mayores reseñas
                shared_words = shared_it
                url = link.get_attribute('href')
        driver.quit()
        return url

    except Exception as e:
        print(e)
        return None
    
def obtener_links_paralelos(recetas):
    """Obtiene enlaces de recetas en paralelo para una lista de recetas.

    Args:
        recetas (list): Lista de nombres de recetas a buscar.

    Returns:
        list: Lista de URLs de las recetas más relevantes encontradas.
    """
    urls = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_receta = {executor.submit(obtener_links, receta): receta for receta in recetas}
        for future in as_completed(future_to_receta):
            receta = future_to_receta[future]
            try:
                url = future.result()
                urls.append(url)
            except Exception as e:
                print(f"Error al obtener link para la receta '{receta}': {e}")
                urls.append(None)

    return urls
    
def clean_texts(texts):
    """Limpia una lista de textos eliminando caracteres no deseados y normalizando el formato.

    Esta función procesa una lista de textos, convirtiéndolos a minúsculas y eliminando cualquier
    parte del texto que aparezca después de los caracteres '#' o '|', así como la palabra 'recipe'.
    Además, se eliminan caracteres no alfanuméricos, reemplazándolos con espacios, y se recortan los
    espacios en blanco al inicio y al final del texto.

    Args:
        texts (list of str): Lista de textos a limpiar.

    Returns:
        list of str: Lista de textos limpiados y normalizados.

    Example:
        >>> clean_texts(["Receta de Galletas #Deliciosas", "Mejor Pastel | receta de chocolate!"])
        ['receta de galletas', 'mejor pastel']
    """
    cleaned_texts = []
    for text in texts:
        text = text.lower()
        text = text.split('#')[0].split('|')[0].split('recipe')[0].split('@')[0]
        cleaned_text = re.sub(r'[^a-zA-Z0-9]+', ' ', text)
        cleaned_texts.append(cleaned_text.strip())
    return cleaned_texts

    
def generate_results(search_term, datefrom=pd.to_datetime('2024')):
    """Genera un DataFrame con los videos más populares relacionados con un término de búsqueda.

    La función realiza una búsqueda de videos mediante una API o librería externa (representada por `Search`), 
    recopilando los títulos, visualizaciones y fechas de publicación de los videos. 
    Filtra los resultados para incluir solo videos publicados después de una fecha dada y elimina duplicados
    según el título, manteniendo el video con mayor número de visualizaciones.

    Args:
        search_term (str): Término de búsqueda para consultar videos relacionados.
        datefrom (datetime, opcional): Fecha mínima para filtrar videos. Por defecto, es el inicio de 2024.

    Returns:
        pd.DataFrame: Un DataFrame con columnas:
            - 'title' (str): Título del video.
            - 'views' (int): Número de visualizaciones del video.
            - 'date' (datetime): Fecha de publicación del video, sin zona horaria.
            
    Raises:
        Exception: Si ocurre algún error durante la obtención de resultados o el procesamiento de datos.
    """

    search = Search(search_term)
    for _ in range(4):
        search.get_next_results()
    dict_videos = dict(title = [], views = [], date = [])
    for video in tqdm(search.videos):
        if video.publish_date.replace(tzinfo=None) > datefrom and video.title not in dict_videos["title"]:
            dict_videos["title"].append(video.title)
            dict_videos["views"].append(video.views)
            dict_videos["date"].append(video.publish_date.replace(tzinfo=None))
    df_videos = pd.DataFrame(dict_videos)
    df_videos = df_videos.iloc[df_videos.sort_values('views', ascending=False)["title"].drop_duplicates().index]
    return df_videos
    
def convert_fractions(ingredient_list):
    """Convierte fracciones en formato Unicode a fracciones numéricas en una lista de ingredientes.

    La función recorre una lista de ingredientes y reemplaza símbolos de fracción en formato Unicode
    (por ejemplo, "½", "⅔") por sus equivalentes numéricos (`Fraction`), facilitando su manipulación numérica
    en análisis posteriores.

    Args:
        ingredient_list (list of str): Lista de ingredientes, cada uno como una cadena de texto.
            Los ingredientes pueden contener fracciones en formato Unicode.

    Returns:
        list of str: Lista de ingredientes con las fracciones Unicode convertidas a su representación
            numérica (`Fraction`). Por ejemplo, "½ taza de azúcar" se convierte a "1/2 taza de azúcar".

    Raises:
        TypeError: Si `ingredient_list` no es una lista de cadenas de texto.

    Example:
        >>> convert_fractions(["½ taza de azúcar", "¼ cucharadita de sal"])
        ['1/2 taza de azúcar', '1/4 cucharadita de sal']
    """

    unicode_fraction_map = {
    "¼": Fraction(1, 4),
    "½": Fraction(1, 2),
    "¾": Fraction(3, 4),
    "⅐": Fraction(1, 7),
    "⅑": Fraction(1, 9),
    "⅒": Fraction(1, 10),
    "⅓": Fraction(1, 3),
    "⅔": Fraction(2, 3),
    "⅕": Fraction(1, 5),
    "⅖": Fraction(2, 5),
    "⅗": Fraction(3, 5),
    "⅘": Fraction(4, 5),
    "⅙": Fraction(1, 6),
    "⅚": Fraction(5, 6),
    "⅛": Fraction(1, 8),
    "⅜": Fraction(3, 8),
    "⅝": Fraction(5, 8),
    "⅞": Fraction(7, 8),
    }
    converted_ingredients = []
    for ingredient in ingredient_list:
        # Find any fraction symbol in the ingredient string
        for symbol, fraction in unicode_fraction_map.items():
            if symbol in ingredient:
                # Replace the symbol with its Fraction value
                ingredient = ingredient.replace(symbol, str(fraction))
        converted_ingredients.append(ingredient)
    return converted_ingredients

def tasty_ing(link):
    """Extrae información de ingredientes de una receta de Tasty.

    Esta función realiza una solicitud a una página de receta de Tasty, 
    extrae el título de la receta, la cantidad de porciones y la lista 
    de ingredientes con sus cantidades y unidades.

    Args:
        link (str): URL de la receta en el sitio de Tasty.

    Returns:
        pd.DataFrame: DataFrame con columnas:
            - 'title' (str): Título de la receta.
            - 'servings' (int): Número de porciones.
            - 'amount' (str): Cantidad del ingrediente (ej. "1/2").
            - 'unit' (str): Unidad de medida (ej. "taza").
            - 'ingredient' (str): Nombre del ingrediente.
            
    Raises:
        requests.exceptions.RequestException: Si ocurre un error en la solicitud a la página.
        AttributeError: Si no se encuentran los elementos esperados en el HTML de la receta.
    """
    response = requests.get(url = link)
    soup = BeautifulSoup(response.content, 'html.parser')
    ingredient_col = soup.find('div', class_ = 'col md-col-4 xs-mx2 xs-pb3 md-mt0 xs-mt2')
    servings = ingredient_col.find('p').text
    ingredient_list = soup.find('div', class_ = 'ingredients__section xs-mt1 xs-mb3').findAll('li')
    amounts_and_ing = []
    for ingredient in ingredient_list:
        parts = ingredient.decode_contents().split('<!-- -->')
        cleaned_parts = [part.strip() for part in parts]
        # print(convert_fractions(cleaned_parts)[0])
        try:
            amount = re.search(pattern = r"\d+\s?\d?/?\d?", string = convert_fractions(cleaned_parts)[0]).group()
        except:
            amount = ""
        try:
            unit = re.search(pattern=r"[A-Za-z]+", string = convert_fractions(cleaned_parts)[0]).group()
        except:
            unit = ""
        element = cleaned_parts[1].split(',')[0].strip().split('<')[0]
        if amount == '':
            element = cleaned_parts[0]
            amount = 1
            unit = 'serving'
        amounts_and_ing.append([amount, unit, element])
    # print(servings)
    df = pd.DataFrame(amounts_and_ing, columns=["amount", "unit", "ingredient"])
    title = soup.find('h1', class_ = 'recipe-name extra-bold xs-mb05 md-mb1')
    
    df.insert(loc = 0, column='servings', value=re.search(pattern = r"\d+", string = servings).group())
    df.insert(loc = 0, column='title', value=title.text)
    return df

    
def allrecipes_ing(link):
    """Extrae información de ingredientes de una receta en Allrecipes.

    Abre la URL de la receta en un navegador usando Selenium, y luego 
    extrae información sobre el título, número de porciones y lista de 
    ingredientes con cantidades y unidades.

    Args:
        link (str): URL de la receta en el sitio de Allrecipes.

    Returns:
        pd.DataFrame: DataFrame con columnas:
            - 'title' (str): Título de la receta.
            - 'servings' (int): Número de porciones.
            - 'amount' (str): Cantidad del ingrediente (ej. "1/2").
            - 'unit' (str): Unidad de medida (ej. "taza").
            - 'ingredient' (str): Nombre del ingrediente.
            
    Raises:
        selenium.common.exceptions.WebDriverException: Si ocurre un error en la conexión o en el controlador.
        AttributeError: Si no se encuentran los elementos esperados en el HTML de la receta.
    """
    driver = webdriver.Chrome()
    driver.get(url = link)
    sleep(2)
    soup2 = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    ingredient_soup = soup2.find('div', class_ = 'comp mm-recipes-structured-ingredients')
    details = soup2.findAll('div', class_ = 'mm-recipes-details__label')
    details_text = np.array([e.text for e in details])
    index = np.where(np.char.find(np.char.lower(details_text), 'serv'.lower()) != -1)[0][0]
    servings = soup2.findAll('div', class_ = 'mm-recipes-details__value')[index]
    ingredient_ul = ingredient_soup.find('ul')
    ingredient_list = ingredient_ul.findAll('li')
    amounts_and_ing = []
    for ingredient in ingredient_list:
        amount = "".join(convert_fractions(ingredient.findAll('span')[0].text))
        unit = ingredient.findAll('span')[1].text
        element = ingredient.findAll('span')[2].text
        amounts_and_ing.append([amount, unit, element])
    
    df = pd.DataFrame(amounts_and_ing, columns=["amount", "unit", "ingredient"])
    title = soup2.find('h1', class_ = 'article-heading type--lion')
    serving_size = re.search(pattern = r"\d+", string = servings.text).group()
    # print(serving_size)
    df.insert(loc = 0, column='servings', value=serving_size)
    df.insert(loc = 0, column='title', value=title.text)
    return df

def edamam_query(df):
    """Genera consultas de ingredientes para la API de Edamam.

    Toma un DataFrame de ingredientes y genera una cadena de texto 
    compatible con la API de Edamam, permitiendo consultar información 
    nutricional de los ingredientes.

    Args:
        df (pd.DataFrame): DataFrame con información de ingredientes.

    Returns:
        list of str: Lista de consultas de ingredientes para la API, 
            cada uno en formato adecuado para Edamam.
            
    Raises:
        ValueError: Si el DataFrame no contiene los campos necesarios.
    """
    ingredientes_str = [" ".join(map(str, item)) for item in df.values]
    return ingredientes_str

def get_nutrients(ing_list, serving_size):
    """Obtiene datos nutricionales de una lista de ingredientes usando la API de EDAMAM.

    Esta función envía una lista de ingredientes a la API de EDAMAM para obtener información
    nutricional detallada para cada ingrediente y ajusta los datos según el tamaño de porción.

    Args:
        ing_list (list): Lista de ingredientes en formato de texto.
        serving_size (int): Tamaño de porción para ajustar los valores nutricionales.

    Returns:
        pd.DataFrame: DataFrame con los nutrientes de cada ingrediente, incluyendo:
            - 'Ingredient' (str): Nombre del ingrediente.
            - 'Weight (g)' (float): Peso en gramos del ingrediente ajustado al tamaño de porción.
            - 'Calories (kcal)' (float): Calorías por porción.
            - 'Protein (g)' (float): Proteína por porción.
            - 'Fat (g)' (float): Grasas por porción.
            - 'Carbohydrates (g)' (float): Carbohidratos por porción.
            - 'Sugar (g)' (float): Azúcar por porción.
            - 'Fiber (g)' (float): Fibra por porción.
            - 'Serving weight (g)' (float): Peso total ajustado al tamaño de porción.

    Raises:
        HTTPError: Si hay un problema en la solicitud a la API de EDAMAM.
    """
    url = "https://api.edamam.com/api/nutrition-details"


    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "ingr": ing_list
        
    }

    response = requests.post(url, headers=headers, 
            params={"app_id": os.getenv('edamam_session_id'), "app_key": os.getenv('edamam_api_key')}, json=data)

    if response.status_code == 200:
        nutrition_data = response.json()
        nutrient_list = []
        for ingredient in nutrition_data.get("ingredients", []):
            try:
                 ingredient.get("parsed")[0] # Para aquellos ingredientes que la api no reconoce
            except:
                continue
            ingredient_name = ingredient.get("parsed")[0].get("foodMatch")
            nutrients = ingredient.get("parsed")[0].get("nutrients")
            weight = ingredient.get("parsed")[0].get("weight")
            total_weight = nutrition_data.get("totalWeight")

            calories = nutrients.get("ENERC_KCAL")["quantity"]
            protein = nutrients.get("PROCNT")["quantity"]
            fat = nutrients.get("FAT")["quantity"]
            carbs = nutrients.get("CHOCDF")["quantity"]
            fiber = nutrients.get("FIBTG")["quantity"]
            try:
                sugar = nutrients.get("SUGAR")["quantity"]
            except:
                sugar = 0
           
            nutrient_list.append({
                "Ingredient": ingredient_name,
                "Weight (g)" : weight/serving_size,
                "Calories (kcal)": calories/serving_size,
                "Protein (g)": protein/serving_size,
                "Fat (g)": fat/serving_size,
                "Carbohydrates (g)": carbs/serving_size,
                "Sugar (g)" : sugar/serving_size,
                "Fiber (g)" : fiber/serving_size,
                "Serving weight (g)" : total_weight/serving_size
            })
        nutrients_df = pd.DataFrame(nutrient_list)
        return nutrients_df

    else:
        print("Error:", response.status_code, response.json())
        return None

def calcular_puntuacion_salud_por_porcion(proteinas, carbohidratos, grasas, fibra, azucar, calorias):
    """Calcula una puntuación de salud para una porción de receta basada en sus macronutrientes.

    Esta función asigna pesos a cada macronutriente y aplica penalizaciones al azúcar y las calorías
    para generar una puntuación de salud, donde una puntuación más alta indica una receta más saludable.

    Args:
        proteinas (float): Cantidad de proteínas en gramos por porción.
        carbohidratos (float): Cantidad de carbohidratos en gramos por porción.
        grasas (float): Cantidad de grasas en gramos por porción.
        fibra (float): Cantidad de fibra en gramos por porción.
        azucar (float): Cantidad de azúcar en gramos por porción.
        calorias (float): Calorías por porción.

    Returns:
        float: Puntuación de salud calculada, donde una puntuación más alta indica un perfil más saludable.
    """
    # Pesos de cada macronutriente
    peso_proteinas = 1.5
    peso_carbohidratos = 1.0
    peso_grasas = 0.8
    peso_fibra = 1.2
    penalizacion_azucar = 1.5
    penalizacion_calorias = 1.0

    # Puntuación de salud en función de la cantidad en un serving
    puntuacion = (
        peso_proteinas * proteinas
        + peso_carbohidratos * carbohidratos
        + peso_grasas * grasas
        + peso_fibra * fibra
        - penalizacion_azucar * azucar
        - penalizacion_calorias * (calorias / 500) # Penalización ajustable sobre las calorías. Cuanto menos, mayor penalización
    )
    return puntuacion
