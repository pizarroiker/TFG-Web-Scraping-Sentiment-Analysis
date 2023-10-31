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
    run_spiders()
    # Obtener los datos de las arañas
    movie_data = sorted(MovieSpider.data, key=lambda x: x['user_reviews_number'], reverse=True)
    movie_data_df = pd.DataFrame(movie_data).drop(columns=['user_reviews_number']).head(50)
    
    tvshow_data = sorted(TvShowsSpider.data, key=lambda x: x['user_reviews_number'], reverse=True)
    tvshow_df = pd.DataFrame(tvshow_data).drop(columns=['user_reviews_number']).head(50)

    # Combinar los datos en una única estructura de datos
    df_combined = pd.concat([movie_data_df, tvshow_df], ignore_index=True)

    # Obtener las reseñas de los URLs
    urls = df_combined['url'].tolist()
    reviews_scraper = ReviewsScraper(urls)
    reviews_data = reviews_scraper.scrape_urls()
    reviews_df = pd.DataFrame(reviews_data, columns=['url', 'reviews'])
    df_combined = df_combined.merge(reviews_df, on='url').drop(columns=['url'])

    # Guardar los datos combinados en un archivo CSV
    df_combined.to_csv("dataset/movies_and_tvshows.csv", index=False, encoding='utf-8')



