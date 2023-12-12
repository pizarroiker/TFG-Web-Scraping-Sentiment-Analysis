from selenium import webdriver
from selenium.webdriver.common.by import By
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ReviewsScraper:

    def __init__(self, urls, op):
        self.urls = urls
        self.op = op
        self.score_selector = self.get_score_selector()

    def get_score_selector(self):
        if self.op == "user":
            return 'div.c-siteReviewScore_background-user span[data-v-4cdca868]'
        elif self.op == "critic":
            return 'div.c-siteReviewScore_background-critic_medium span[data-v-4cdca868]'

    def scrape_reviews(self, url, driver, max_reviews=20, target_language='en'):
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.c-siteReview.g-bg-gray10')))
        reviews = set()
        review_elements = driver.find_elements(By.CSS_SELECTOR,'div.c-siteReview.g-bg-gray10')
        
        for review_element in review_elements:
            if len(reviews) >= max_reviews:
                break
            score, text = self.extract_review_data(review_element)
            if self.is_valid_review(text, score):
                detected_language = self.safe_language_detection(text)
                if detected_language == target_language:
                    reviews.add((score, text))
        return reviews

    def extract_review_data(self, review_element):
        score = review_element.find_element(By.CSS_SELECTOR, self.score_selector).text
        text = review_element.find_element(By.CSS_SELECTOR,'div.c-siteReview_quote span').text
        if self.op == "critic":
            score = round(int(score) / 10, 1)
        return score, text

    def is_valid_review(self, text, score):
        spoiler_text = "[SPOILER ALERT: This review contains spoilers.]"
        censored_words = ["****", "*****", "******"]
        return all(censored_word not in text for censored_word in censored_words) and text != spoiler_text and len(text) >= 10

    def safe_language_detection(self, text):
        try:
            return detect(text)
        except LangDetectException:
            return "unknown"

    def configure_webdriver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--blink-settings=imagesEnabled=false")
        return options

    def scrape_urls(self):
        with webdriver.Chrome(options=self.configure_webdriver()) as driver:
            scraped_urls = [(url, self.scrape_reviews(url, driver)) for url in self.urls]
        return scraped_urls


