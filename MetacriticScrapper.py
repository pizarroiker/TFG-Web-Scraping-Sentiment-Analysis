# Description: Este archivo contiene el código para ejecutar las arañas de Scrapy y guardar los datos en un archivo CSV.

from scrapy.crawler import CrawlerProcess
import pandas as pd
from Spiders.MovieSpider import MovieSpider
from Spiders.TVShowsSpider import TvShowsSpider
from Spiders.ReviewsScrapper import ReviewsScraper

def min_converter(duration):
    if duration:
        duracion = duration.split()
        if len(duracion) == 2:
            if duracion[1] == "h":
                return int(duracion[0]) * 60
            elif duracion[1] == "min":
                return int(duracion[0])
        elif len(duracion) == 4:
            return int(duracion[0]) * 60 + int(duracion[2])
    return None

def run_spiders():
    # Crear una instancia del proceso Crawler
    process = CrawlerProcess(settings={
        "CONCURRENT_REQUESTS": 32,
    })

    # Agregar los Spiders al proceso
    process.crawl(MovieSpider)
    process.crawl(TvShowsSpider)

    # Iniciar el proceso, pero detenerlo después de que ambas arañas hayan terminado
    process.start(stop_after_crawl=True)
    
if __name__ == "__main__":
    
    #-----------------------------------------------------#
    #           PROCESO DE EXTRACCIóN DE DATOS            #
    #-----------------------------------------------------#
    
    # Ejecutar las arañas
    run_spiders()
    
    # Obtener los datos de ambas arañas
    movie_data = sorted(MovieSpider.data, key=lambda x: x['reviews_number'], reverse=True)
    movie_data_df = pd.DataFrame(movie_data).drop(columns=['reviews_number']).head(50)
    
    tvshow_data = sorted(TvShowsSpider.data, key=lambda x: x['reviews_number'], reverse=True)
    tvshow_df = pd.DataFrame(tvshow_data).drop(columns=['reviews_number']).head(50)

    # Combinar los datos en una única estructura de datos
    df = pd.concat([movie_data_df, tvshow_df], ignore_index=True)

    # Obtener las reseñas de las URLs
    user_urls = df['user_reviews_url'].tolist()
    critic_urls = df['critic_reviews_url'].tolist()
    user_reviews_scraper = ReviewsScraper(user_urls,"user")
    critic_reviews_scraper = ReviewsScraper(critic_urls,"critic")
    user_reviews_data = user_reviews_scraper.scrape_urls()
    critic_reviews_data = critic_reviews_scraper.scrape_urls()
    user_reviews_df = pd.DataFrame(user_reviews_data, columns=['user_reviews_url', 'user_reviews'])
    critic_reviews_df = pd.DataFrame(critic_reviews_data, columns=['critic_reviews_url', 'critic_reviews'])
    df = df.merge(user_reviews_df, on='user_reviews_url').drop(columns=['user_reviews_url'])
    df = df.merge(critic_reviews_df, on='critic_reviews_url').drop(columns=['critic_reviews_url'])
    
    #-----------------------------------------------------#
    #            PROCESO DE LIMPIEZA DE DATOS             #
    #-----------------------------------------------------#
    
    # Convertir las fecha de lanzamiento a formato datetime
    df["release_date"] = pd.to_datetime(df["release_date"])
    
    # Convertir la columna géneros a varias columnas binarias con cada género
    # De esta manera facilitamos el análisis de los datos por género
    generos_unicos = set( [genero for lista in df["genres"] for genero in lista] )
    for genero in generos_unicos:
        df[genero] = df["genres"].apply(lambda x: 1 if genero in x else 0)
    df = df.drop('genres', axis=1)
    
    # Convertir la duración de los item de tipo película a minutos    
    df.loc[df['type'] == 'movie', 'duration'] = df.loc[df['type'] == 'movie', 'duration'].apply(min_converter)
    
    # Convertir la duración de los item de tipo serie a numero de temporadas
    df.loc[df['type'] == 'tvshow', 'duration'] = df.loc[df['type'] == 'tvshow', 'duration'].apply(lambda x: int(x.split()[0]))    

    #-----------------------------------------------------#
    #            PROCESO DE VOLCADO DE DATOS              #
    #-----------------------------------------------------#
    
    df.to_csv("dataset/movies_and_tvshows.csv", index=False, encoding='utf-8')



