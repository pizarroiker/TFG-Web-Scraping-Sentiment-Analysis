from scrapy.crawler import CrawlerProcess
import pandas as pd
from Spiders.MovieSpider import MovieSpider
from Spiders.TVShowsSpider import TvShowsSpider
from Spiders.ReviewsScrapper import ReviewsScraper

# Constantes
TOP_ITEMS = 50
CRAWLER_SETTINGS = {"CONCURRENT_REQUESTS": 32}

def min_converter(duration):
    """
    Convierte la duración en formato 'X h Y min' a minutos.
    Args:
    - duration (str): Duración en formato 'X h Y min' o similar.
    Returns:
    - int: Duración en minutos.
    """
    if duration:
        parts = duration.split()
        hours = int(parts[0]) * 60 if 'h' in parts else 0
        minutes = int(parts[parts.index('min') - 1]) if 'min' in parts else 0
        return hours + minutes
    return None

def run_spiders():
    """
    Inicia el proceso de scraping usando las arañas definidas en la carpeta scrapper.
    """
    process = CrawlerProcess(settings=CRAWLER_SETTINGS)
    process.crawl(MovieSpider)
    process.crawl(TvShowsSpider)
    process.start(stop_after_crawl=True)

def get_top_data(spider, columns_to_drop):
    """
    Obtiene los datos de una araña y retorna un dataframe con los TOP_ITEMS primeros elementos.
    Args:
    - spider: Instancia de una araña de Scrapy.
    - columns_to_drop (list): Columnas a eliminar del dataframe.
    Returns:
    - DataFrame: Datos procesados en un dataframe.
    """
    data = sorted(spider.data, key=lambda x: x['reviews_number'], reverse=True)
    return pd.DataFrame(data).drop(columns=columns_to_drop).head(TOP_ITEMS)

def merge_dataframes(df1, df2):
    """
    Combina dos dataframes en uno.
    Args:
    - df1, df2 (DataFrame): Dataframes a combinar.
    Returns:
    - DataFrame: Dataframe combinado.
    """
    return pd.concat([df1, df2], ignore_index=True)

def scrape_reviews(df):
    """
    Scrapea y agrega reseñas de usuarios y críticos a un dataframe.
    Args:
    - df (DataFrame): Dataframe con URLs de reseñas.
    Returns:
    - DataFrame: Dataframe actualizado con reseñas.
    """
    user_reviews_scraper = ReviewsScraper(df['user_reviews_url'].tolist(), "user")
    critic_reviews_scraper = ReviewsScraper(df['critic_reviews_url'].tolist(), "critic")

    user_reviews = user_reviews_scraper.scrape_urls()
    critic_reviews = critic_reviews_scraper.scrape_urls()

    user_reviews_df = pd.DataFrame(user_reviews, columns=['user_reviews_url', 'user_reviews'])
    critic_reviews_df = pd.DataFrame(critic_reviews, columns=['critic_reviews_url', 'critic_reviews'])

    df = df.merge(user_reviews_df, on='user_reviews_url').drop(columns=['user_reviews_url'])
    return df.merge(critic_reviews_df, on='critic_reviews_url').drop(columns=['critic_reviews_url'])

def process_data(df):
    """
    Procesa los datos del dataframe aplicando varias transformaciones.
    Args:
    - df (DataFrame): Dataframe a procesar.
    Returns:
    - DataFrame: Dataframe procesado.
    """
    # Convertir fechas a datetime
    df["release_date"] = pd.to_datetime(df["release_date"])

    # Procesamiento de géneros
    all_genres = set(genre for genres_list in df["genres"] for genre in genres_list)
    for genre in all_genres:
        df[genre] = df["genres"].apply(lambda x: 1 if genre in x else 0)
    df.drop('genres', axis=1, inplace=True)

    # Conversión de duración
    df.loc[df['type'] == 'movie', 'duration'] = df.loc[df['type'] == 'movie', 'duration'].apply(min_converter)
    df.loc[df['type'] == 'tvshow', 'duration'] = df.loc[df['type'] == 'tvshow', 'duration'].apply(lambda x: int(x.split()[0]))

    return df

def save_data(df, filepath):
    """
    Guarda un dataframe en un archivo CSV.
    Args:
    - df (DataFrame): Dataframe a guardar.
    - filepath (str): Ruta del archivo CSV.
    """
    df.to_csv(filepath, index=False, encoding='utf-8')


# PROGRAMA PRINCIPAL
if __name__ == "__main__":
    
    # Proceso de scraping
    run_spiders()
    movie_df = get_top_data(MovieSpider, ['reviews_number'])
    tvshow_df = get_top_data(TvShowsSpider, ['reviews_number'])
    combined_df = merge_dataframes(movie_df, tvshow_df)
    combined_df = scrape_reviews(combined_df)
    
    # Procesamiento de datos
    combined_df = process_data(combined_df)
    
    # Guardar datos
    save_data(combined_df,"dataset/movies_and_tvshows.csv")



