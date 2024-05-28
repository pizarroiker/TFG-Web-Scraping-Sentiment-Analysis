# Importaciones de módulos necesarios
from scrapy.crawler import CrawlerProcess
import pandas as pd
from Spiders.MovieSpider import MovieSpider
from Spiders.TVShowsSpider import TvShowsSpider
from Spiders.ReviewsScrapper import ReviewsScraper


# Definición de constantes globales
TOP_ITEMS = 5                                       # Número máximo de elementos a procesar de cada tipo
YEAR = 2023                                         # Año para el cual se realizará el scraping
CRAWLER_SETTINGS = {"CONCURRENT_REQUESTS": 32}      # Configuración para el proceso de crawling


# Función para iniciar el proceso de scraping
def run_spiders():
    # Inicia el proceso de crawling utilizando Scrapy
    process = CrawlerProcess(settings=CRAWLER_SETTINGS)
    # Agrega arañas (spiders) para películas y programas de TV
    process.crawl(MovieSpider, year=YEAR)   
    process.crawl(TvShowsSpider, year=YEAR)
    # Inicia el proceso de scraping y se detiene automáticamente después
    process.start(stop_after_crawl=True)


# Función para procesar los datos recopilados por una araña
def process_spider_data_reviews(data, columns_to_drop):
    # Filtra los datos según la cantidad de reseñas de usuarios y críticos
    data = data[(data['user_reviews_number'] > 50) & (data['critic_reviews_number'] > 20)]
    
    # Crea un DataFrame de pandas a partir de los datos recolectados
    data = process_spider_data(data, columns_to_drop)
    
    # Devuelve los mejores elementos
    return data.head(TOP_ITEMS)


def process_spider_data(data, columns_to_drop):  
    # Convierte la fecha de lanzamiento a un formato de fecha
    data["release_date"] = pd.to_datetime(data["release_date"], format="mixed")
    
    # Limpiar valores atipicos de la fecha de lanzamiento
    data = data[(data["release_date"].dt.year == YEAR)]
    
    # Elimina las columnas no deseadas
    data.drop(columns=columns_to_drop, inplace=True, errors='ignore')
    
    # Convierte las puntuaciones a números y escala el metascore a un numero entre el 1 y el 10
    data['metascore'] = pd.to_numeric(data['metascore'], errors='coerce') / 10
    data['user_score'] = pd.to_numeric(data['user_score'], errors='coerce')
     # Calcula una puntuación ponderada y la añade al DataFrame
    data['weighted_score'] = round((data['metascore'] * 0.3) + (data['user_score'] * 0.7), 1)
    # Ordena los datos y devuelve los mejores elementos
    return data.sort_values(by='weighted_score', ascending=False)


# Función para combinar dos DataFrames
def merge_dataframes(df1, df2):
    # Combina dos DataFrames en uno solo
    return pd.concat([df1, df2], ignore_index=True)


# Función para raspar reseñas desde URLs proporcionadas
def scrape_reviews(urls, review_type):
     # Inicializa el raspador de reseñas con las URLs y el tipo de reseña (usuario o crítico)
    scraper = ReviewsScraper(urls, review_type)
    # Realiza el scraping y retorna los resultados como un DataFrame
    return pd.DataFrame(scraper.scrape_urls(), columns=[f'{review_type}_reviews_url', f'{review_type}_reviews'])


# Función para combinar las reseñas con los datos principales
def merge_reviews_with_data(df):
    # Scrapea reseñas de usuarios y críticos y las convierte en DataFrames
    user_reviews_df = scrape_reviews(df['user_reviews_url'].tolist(), "user")    
    critic_reviews_df = scrape_reviews(df['critic_reviews_url'].tolist(), "critic")
    # Combina los DataFrames de reseñas con el DataFrame principal
    df = df.merge(user_reviews_df, on='user_reviews_url').drop(columns=['user_reviews_url'])
    return df.merge(critic_reviews_df, on='critic_reviews_url').drop(columns=['critic_reviews_url'])


# Función para guardar un DataFrame en un archivo CSV
def save_data(df, filepath):
    # Guarda el DataFrame en un archivo CSV en la ruta especificada
    df.to_csv(filepath, index=False, encoding='utf-8')


# Programa principal
if __name__ == "__main__":
    # Inicia el proceso de scraping
    run_spiders()

    # Obtiene los datos recopilados por las arañas para películas y programas de TV
    movie_df = pd.DataFrame(MovieSpider.data)
    tvshow_df = pd.DataFrame(TvShowsSpider.data)
    
    # Procesa los datos recopilados por las arañas para películas y programas de TV para su análisis
    movies = process_spider_data(movie_df, ['user_reviews_number', 'critic_reviews_number', 'user_reviews_url', 'critic_reviews_url'])
    tvshows = process_spider_data(tvshow_df, ['user_reviews_number', 'critic_reviews_number', 'user_reviews_url', 'critic_reviews_url'])

    # Procesa los datos recopilados por las arañas para películas y programas de TV para la posterior incorporación de reseñas
    movie_reviews = process_spider_data_reviews(movie_df, ['user_reviews_number', 'critic_reviews_number'])
    tvshow__reviews = process_spider_data_reviews(tvshow_df, ['user_reviews_number', 'critic_reviews_number'])
    
    # Combina los DataFrames de películas y programas de TV
    combined_df = merge_dataframes(movies, tvshows)
    #Combina los DataFrames de películas y programas de TV para la posterior incorporación de reseñas
    combined_reviews_df = merge_dataframes(movie_reviews, tvshow__reviews)
    # Combina los DataFrames de reseñas con el DataFrame principal
    combined_reviews_df = merge_reviews_with_data(combined_reviews_df)
    # Guarda el DataFrame combinado de películas y series en un archivo CSV
    save_data(combined_df, "dataset/movies_and_tvshows.csv")
    # Guarda el DataFrame combinado de películas, series y reseñas en un archivo CSV
    save_data(combined_reviews_df, "dataset/top_items_reviews.csv")