# Description: Este archivo contiene el código para ejecutar las arañas de Scrapy y guardar los datos en un archivo CSV.

from scrapy.crawler import CrawlerProcess
import pandas as pd
from Spiders.MovieSpider import MovieSpider
from Spiders.TVShowsSpider import TvShowsSpider
from Spiders.ReviewsScrapper import ReviewsScraper

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
    df_combined = pd.concat([movie_data_df, tvshow_df], ignore_index=True)

    # Obtener las reseñas de las URLs
    user_urls = df_combined['user_reviews_url'].tolist()
    critic_urls = df_combined['critic_reviews_url'].tolist()
    user_reviews_scraper = ReviewsScraper(user_urls,"user")
    critic_reviews_scraper = ReviewsScraper(critic_urls,"critic")
    user_reviews_data = user_reviews_scraper.scrape_urls()
    critic_reviews_data = critic_reviews_scraper.scrape_urls()
    user_reviews_df = pd.DataFrame(user_reviews_data, columns=['user_reviews_url', 'user_reviews'])
    critic_reviews_df = pd.DataFrame(critic_reviews_data, columns=['critic_reviews_url', 'critic_reviews'])
    df_combined = df_combined.merge(user_reviews_df, on='user_reviews_url').drop(columns=['user_reviews_url'])
    df_combined = df_combined.merge(critic_reviews_df, on='critic_reviews_url').drop(columns=['critic_reviews_url'])
    
    #-----------------------------------------------------#
    #            PROCESO DE LIMPIEZA DE DATOS             #
    #-----------------------------------------------------#
    
    
    
    #-----------------------------------------------------#
    #            PROCESO DE VOLCADO DE DATOS              #
    #-----------------------------------------------------#
    
    df_combined.to_csv("dataset/movies_and_tvshows.csv", index=False, encoding='utf-8')



