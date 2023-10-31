from selenium import webdriver
from selenium.webdriver.common.by import By
from langdetect import detect  # Importa la función detect de langdetect
from langdetect.lang_detect_exception import LangDetectException

class ReviewsScraper:
    
    def __init__(self, urls):
        # Inicializa la lista de URLs al crear el objeto
        self.urls = urls

    def scrape_reviews(self, url, driver, max_reviews=20, target_language='en'):
        # Abre la URL en el navegador
        driver.get(url)
        
        # Lista para almacenar las reseñas únicas
        reviews = set()
        
        # Extrae los elementos de reseña de la página
        review_elements = driver.find_elements(By.CSS_SELECTOR, 'div.c-siteReview.g-bg-gray10')
        
        # Almacenamos los selectores en variables para evitar repeticiones
        score_selector = 'div.c-siteReviewScore_background-user span[data-v-4cdca868]'
        text_selector = 'div.c-siteReview_quote span'
        
        # Texto que indica que la reseña contiene spoilers o palabras malsonantes
        spoiler_text = "[SPOILER ALERT: This review contains spoilers.]"
        censored_words = ["****", "*****", "******"]
        
        # Itera a través de los elementos de reseña y extrae la información
        for review_element in review_elements:
            # Si hemos alcanzado el límite de 20 reseñas, salimos del bucle
            if len(reviews) >= max_reviews:
                break
            
            # Extrae la nota de usuario y el contenido de la reseña
            score = review_element.find_element(By.CSS_SELECTOR, score_selector).text
            text = review_element.find_element(By.CSS_SELECTOR, text_selector).text 
            
            # Verifica si el texto de la reseña contiene palabras censuradas
            if any(censored_word in text for censored_word in censored_words) or text == spoiler_text:
                continue  # Ignora reseñas con palabras censuradas o spoilers
            
            if len(text) >= 10:
                # Utiliza langdetect para detectar el idioma de la reseña
                detected_language = self.safe_language_detection(text)
                
                if detected_language == target_language:
                    reviews.add((score, text))
                
        return reviews

    def safe_language_detection(self, text):
        try:
            detected_language = detect(text)
            return detected_language
        except LangDetectException as e:
            return "unknown"

    def configure_webdriver(self):
        # Configura las opciones del navegador
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--blink-settings=imagesEnabled=false")
        return options
    
    def scrape_urls(self):
        # Inicia el navegador
        driver = webdriver.Chrome(options=self.configure_webdriver())
        
        # Lista para almacenar las URLs y reseñas
        scraped_urls = []
        
        # Itera a través de las URLs
        for url in self.urls:
            # Extrae las reseñas de la URL y las almacena en una lista
            scraped_reviews = self.scrape_reviews(url,driver)
            scraped_urls.append((url,scraped_reviews))
            
        # Cierra el navegador
        driver.quit()
        
        # Devuelve la lista de URLs y reseñas
        return scraped_urls

