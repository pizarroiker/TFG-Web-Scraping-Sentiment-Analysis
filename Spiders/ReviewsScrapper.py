from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

class ReviewsScraper:

    def __init__(self, urls, op):
        self.urls = urls  # Lista de URLs a scrapear
        self.op = op  # Tipo de operación: "user" o "critic"
        self.score_selector = self.get_score_selector()  # Selector CSS para la puntuación
        self.referer_url = 'https://www.metacritic.com/'  # URL de referencia

    def get_score_selector(self):
        # Retorna el selector CSS adecuado según el tipo de operación
        if self.op == "user":
            return 'div.c-siteReviewScore_background-user span[data-v-4cdca868]'
        elif self.op == "critic":
            return 'div.c-siteReviewScore_background-critic_medium span[data-v-4cdca868]'

    def scrape_reviews(self, url, driver, max_reviews=30, target_language='en'):
        driver.get(url)  # Abre la URL con el navegador
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.c-siteReview.g-bg-gray10')))  # Espera hasta que los elementos de las reseñas sean visibles
        reviews = []  # Lista para almacenar las reseñas
        review_elements = driver.find_elements(By.CSS_SELECTOR,'div.c-siteReview.g-bg-gray10')  # Encuentra los elementos de las reseñas
        
        for review_element in review_elements:
            if len(reviews) >= max_reviews:  # Limita el número de reseñas a extraer
                break
            score, text = self.extract_review_data(review_element)  # Extrae la puntuación y el texto de la reseña
            if self.is_valid_review(text, score):  # Verifica si la reseña es válida
                detected_language = self.safe_language_detection(text)  # Detecta el idioma del texto de la reseña
                if detected_language == target_language:  # Filtra las reseñas por idioma
                    reviews.append((score, text))
        return reviews  # Retorna las reseñas extraídas

    def extract_review_data(self, review_element):
        # Extrae la puntuación y el texto de una reseña
        score = review_element.find_element(By.CSS_SELECTOR, self.score_selector).text
        text = review_element.find_element(By.CSS_SELECTOR,'div.c-siteReview_quote span').text
        if self.op == "critic":
            score = round(int(score) / 10, 1)  # Ajusta la puntuación si es de un crítico
        return score, text

    def is_valid_review(self, text, score):
        # Verifica si una reseña es válida basándose en ciertas condiciones
        spoiler_text = "[SPOILER ALERT: This review contains spoilers.]"
        censored_words = ["****", "*****", "******"]
        return all(censored_word not in text for censored_word in censored_words) and text != spoiler_text and len(text) >= 10

    def safe_language_detection(self, text):
        # Detecta el idioma del texto de manera segura
        try:
            return detect(text)
        except LangDetectException:
            return "unknown"

    def configure_webdriver(self):
        # Configura las opciones del WebDriver para Selenium
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Ejecuta en modo headless (sin interfaz gráfica)
        options.add_argument("--disable-gpu")  # Desactiva la GPU
        options.add_argument("--disable-extensions")  # Desactiva las extensiones del navegador
        options.add_argument("--blink-settings=imagesEnabled=false")  # Desactiva la carga de imágenes
        options.add_argument(f"--referer={self.referer_url}")  # Añade el referer a las opciones del navegador
        return options

    def scrape_urls(self):
        # Configura el WebDriver y scrapea las URLs
        options = self.configure_webdriver()
        with webdriver.Chrome(options=options) as driver:
            # Recorre las URLs y extrae las reseñas para cada una
            scraped_urls = [(url, self.scrape_reviews(url, driver)) for url in self.urls]
        return scraped_urls  # Retorna las URLs junto con las reseñas extraídas
