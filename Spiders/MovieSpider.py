import scrapy
import re

class MovieSpider(scrapy.Spider):
    name = "movie_spider"
    start_urls = [f'https://www.metacritic.com/browse/movie/all/all/current-year/?page={page}' for page in range(1, 30)]
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    data = [] # Lista para almacenar los datos

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, headers={'User-Agent': self.user_agent})

    def parse(self, response):
        for item in response.css('div.c-finderProductCard'):
            url = item.css('a.c-finderProductCard_container::attr(href)').get()
            if url:
                yield response.follow(url, self.parse_item)

    def parse_item(self, response):
        def extract_text(selector):
            return response.css(selector).get(default='').strip()

        title = extract_text('div.c-productHero_title div::text')
        metascore = extract_text('div.c-siteReviewScore_background-critic_medium span[data-v-4cdca868]::text')
        user_score = extract_text('div.c-siteReviewScore_background-user span[data-v-4cdca868]::text')
        release_date = extract_text('div.c-movieDetails_sectionContainer span.g-text-bold:contains("Release Date") + span::text')
        duration = extract_text('div.c-movieDetails_sectionContainer span.g-text-bold:contains("Duration") + span::text')
        user_reviews_text = extract_text('span.c-productScoreInfo_reviewsTotal a span::text')
        url = response.url + "user-reviews/"
        if user_reviews_text:
            user_reviews_number = int(re.search(r'\d+', user_reviews_text).group())
        if user_score != "tbd" and metascore != "tbd":
            movie_data = {
                'title': title,
                'release_date': release_date,
                'duration': duration,
                'metascore': metascore,
                'user_score': user_score,
                'user_reviews_number': user_reviews_number,
                'url': url
            }
            self.data.append(movie_data)


