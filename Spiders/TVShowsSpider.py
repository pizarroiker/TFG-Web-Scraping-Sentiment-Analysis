import scrapy
import re

#Clase para extraer los datos de las series de la página de Metacritic
class TvShowsSpider(scrapy.Spider):
    
    # Nombre de la araña (spider)
    name = "tvshows_spider"
    
    # URLs de inicio, generadas para obtener datos de series del año actual en 30 páginas
    start_urls = [f'https://www.metacritic.com/browse/tv/all/all/current-year/?page={page}' for page in range(1, 30)]
    
    # Agente de usuario simulando ser un navegador Chrome en Windows
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    
    # Lista para almacenar las series
    data = []  
    
    # Método para iniciar las solicitudes a cada página y asignar el agente de usuario
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, headers={'User-Agent': self.user_agent})

    # Método para analizar la respuesta a la página y seguir los enlaces a las páginas principales de cada serie
    def parse(self, response):
        for item in response.css('div.c-finderProductCard'):
            url = item.css('a.c-finderProductCard_container::attr(href)').get()
            if url:
                yield response.follow(url, self.parse_item)

    # Método para analizar la página principal de una serie y extraer la información necesaria
    def parse_item(self, response):
        
        # Función interna para extraer texto de un selector con opción de valor por defecto
        def extract_text(selector,response = response):
            return response.css(selector).get(default='').strip()

        try:
            # Extracción de datos de la serie
            title = extract_text('div.c-productHero_title div::text')
            metascore = extract_text('div.c-siteReviewScore_background-critic_medium span[data-v-4cdca868]::text')
            user_score = extract_text('div.c-siteReviewScore_background-user span[data-v-4cdca868]::text')
            release_date = extract_text('div.c-productionDetailsTv_details span.g-text-bold:contains("Initial Release Date:") + span::text')
            duration = extract_text('div.c-productionDetailsTv_details span.g-text-bold:contains("Number of seasons:") + span::text')
            reviews_text = extract_text('span.c-productScoreInfo_reviewsTotal a span::text')
            user_url = response.url + "user-reviews/"
            critic_url = response.url + "critic-reviews/"

            # Extracción de géneros de la serie
            genres = [extract_text('span.c-globalButton_label::text', genre) for genre in response.css('ul.c-genreList')[-1].css('li')]
            
            # Conteo de la cantidad de reseñas de usuarios y críticos
            reviews_number =sum(int(re.search(r'\d+', reviews_text).group()) for text in reviews_text if text)  
            
            # Verificación de que los puntajes no sean "tbd" (To Be Determined)  
            if user_score != "tbd" and metascore != "tbd":
                # Creación de un diccionario con los datos de la serie
                tvshow_data = {
                    'title': title,
                    'release_date': release_date,
                    'duration': duration,
                    'metascore': metascore,
                    'user_score': user_score,
                    'genres': genres,
                    'user_reviews_url': user_url,
                    'critic_reviews_url': critic_url,
                    'reviews_number': reviews_number
                }
                self.data.append(tvshow_data)
        # Control de errores
        except Exception as e:
            self.log(f"Error processing {response.url}: {str(e)}")