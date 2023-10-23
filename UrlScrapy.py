import scrapy
from scrapy.crawler import CrawlerProcess

class MetacriticSpider(scrapy.Spider):
    name = "metacritic_spider"
    start_urls = ['https://www.metacritic.com/browse/{category}/all/all/{year}/metascore?page={page}'.format(category=category, year=year, page=page) for category in ['movie', 'tv'] for year in range(2021, 2024) for page in range(1, 101)]

    def parse(self, response):
        for item in response.css('div.c-finderProductCard'):
            yield {
                'url': item.css('a.c-finderProductCard_container::attr(href)').get()
            }

process = CrawlerProcess(settings={
    "FEEDS": {
        "./moviesurls.csv": {"format": "csv", "overwrite": True},
    },
})

process.crawl(MetacriticSpider)
process.start()

