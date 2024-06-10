import scrapy
import re

class MovieSpider(scrapy.Spider):
    name = "movie_spider"  # Nombre del spider                 
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'  # Agente de usuario para las solicitudes HTTP
    referer = 'https://www.metacritic.com/'  # Referente para las solicitudes HTTP
    headers = {'User-Agent': user_agent, 'Referer': referer}  # Encabezados HTTP personalizados
    data = []  # Lista para almacenar los datos extraídos

    def __init__(self, year):
        self.year = year  # Año para filtrar las películas
        # URLs de inicio para cada página de resultados en Metacritic para el año especificado
        self.start_urls = [f'https://www.metacritic.com/browse/movie/all/all/{self.year}/new/?page={page}' for page in range(1, 50)]
    
    def start_requests(self):
        # Generar solicitudes HTTP para cada URL de inicio con los encabezados personalizados
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        # Extraer cada tarjeta de producto en la página de resultados
        for item in response.css('div.c-finderProductCard'):
            # Extraer la URL de la página del detalle de la película
            url = item.css('a.c-finderProductCard_container::attr(href)').get()
            if url:
                # Seguir la URL y procesar el detalle de la película con el método parse_item
                yield response.follow(url, self.parse_item)

    def parse_item(self, response):
        # Función auxiliar para extraer texto de un selector CSS
        def extract_text(selector, response=response):
            return response.css(selector).get('').strip()

        try:
            # Selectores CSS para extraer la información relevante
            title_selector = 'div.c-productHero_title h1::text'
            metascore_selector = 'div.c-siteReviewScore_background-critic_medium span[data-v-4cdca868]::text'
            user_score_selector = 'div.c-siteReviewScore_background-user span[data-v-4cdca868]::text'
            release_date_selector = 'div.c-movieDetails_sectionContainer span.g-text-bold:contains("Release Date") + span::text'
            duration_selector = 'div.c-movieDetails_sectionContainer span.g-text-bold:contains("Duration") + span::text'
            reviews_text_selector = 'span.c-productScoreInfo_reviewsTotal a span::text'
            genre_selector = 'span.c-globalButton_label::text'

            # Extraer la información de los selectores
            title = extract_text(title_selector)
            metascore = extract_text(metascore_selector)
            user_score = extract_text(user_score_selector)
            release_date = extract_text(release_date_selector)
            duration = extract_text(duration_selector)
            reviews_text = response.css(reviews_text_selector).getall()
            genres = {extract_text(genre_selector, genre) for genre in response.css('ul.c-genreList')[0].css('li')}

            critic_reviews_number = 0
            user_reviews_number = 0
            if reviews_text and len(reviews_text) > 1:
                # Extraer el número de críticas de los textos extraídos utilizando expresiones regulares
                critic_reviews_number = int(re.search(r'[\d,]+', reviews_text[0]).group().replace(',', ''))
                user_reviews_number = int(re.search(r'[\d,]+', reviews_text[1]).group().replace(',', ''))
            
            if user_score != "tbd" and metascore != "tbd":
                # Crear un diccionario con la información de la película
                movie_data = {
                    'title': title,
                    'release_date': release_date,
                    'type': "movie",
                    'duration': duration,
                    'metascore': metascore,
                    'user_score': user_score,
                    'genres': genres,
                    'user_reviews_url': response.url + "user-reviews/",
                    'critic_reviews_url': response.url + "critic-reviews/",
                    'user_reviews_number': user_reviews_number,
                    'critic_reviews_number': critic_reviews_number
                }
                # Agregar la información de la película a la lista de datos
                self.data.append(movie_data)
        except ValueError as e:
            # Registrar cualquier error encontrado durante el procesamiento
            self.log(f"Error processing {response.url}: {str(e)}")
