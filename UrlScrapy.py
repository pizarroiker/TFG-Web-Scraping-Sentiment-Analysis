import scrapy
from scrapy.crawler import CrawlerProcess

class MetacriticSpider(scrapy.Spider):
    name = "metacritic_spider"
    start_urls = ['https://www.metacritic.com/browse/{category}/?releaseYearMin=2019&releaseYearMax=2023&page={page}'.format(category=category, page=page) for category in ["movie","tv"] for page in range(1, 101)]
    visited_urls = set()

    def parse(self, response):
        for item in response.css('div.c-finderProductCard'):
            url = item.css('a.c-finderProductCard_container::attr(href)').get()
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                yield {
                    'url': url
                }

process = CrawlerProcess(settings={
    "FEEDS": {
        "./moviesurls.csv": {"format": "csv", "overwrite": True},
    },
})

process.crawl(MetacriticSpider)
process.start()

