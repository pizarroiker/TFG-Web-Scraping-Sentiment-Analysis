import scrapy
import re

class MovieSpider(scrapy.Spider):
    name = "movie_spider"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    data = []

    def __init__(self, year):
        self.year = year
        self.start_urls = [f'https://www.metacritic.com/browse/movie/all/all/{self.year}/?page={page}' for page in range(1, 30)]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, headers={'User-Agent': self.user_agent})

    def parse(self, response):
        for item in response.css('div.c-finderProductCard'):
            url = item.css('a.c-finderProductCard_container::attr(href)').get()
            if url:
                yield response.follow(url, self.parse_item)

    def parse_item(self, response):
        def extract_text(selector, default=''):
            return response.css(selector).get(default=default).strip()

        try:
            title_selector = 'div.c-productHero_title div::text'
            metascore_selector = 'div.c-siteReviewScore_background-critic_medium span[data-v-4cdca868]::text'
            user_score_selector = 'div.c-siteReviewScore_background-user span[data-v-4cdca868]::text'
            release_date_selector = 'div.c-movieDetails_sectionContainer span.g-text-bold:contains("Release Date") + span::text'
            duration_selector = 'div.c-movieDetails_sectionContainer span.g-text-bold:contains("Duration") + span::text'
            reviews_text_selector = 'span.c-productScoreInfo_reviewsTotal a span::text'
            genre_selector = 'span.c-globalButton_label::text'

            title = extract_text(title_selector)
            metascore = extract_text(metascore_selector)
            user_score = extract_text(user_score_selector)
            release_date = extract_text(release_date_selector)
            duration = extract_text(duration_selector)
            reviews_text = response.css(reviews_text_selector).getall()
            genres = [extract_text(genre_selector, genre) for genre in response.css('ul.c-genreList')[-1].css('li')]

            critic_reviews_number=0
            user_reviews_number=0
            if reviews_text and len(reviews_text) > 1:
                critic_reviews_number = int(re.search(r'\d+', reviews_text[0]).group())
                user_reviews_number = int(re.search(r'\d+', reviews_text[1]).group())
            
            if user_score != "tbd" and metascore != "tbd":
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
                self.data.append(movie_data)
        except ValueError as e:
            self.log(f"Error processing {response.url}: {str(e)}")



