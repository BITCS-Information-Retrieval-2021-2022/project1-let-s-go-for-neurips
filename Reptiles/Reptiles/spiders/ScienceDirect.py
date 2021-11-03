import scrapy


class SciencedirectSpider(scrapy.Spider):
    name = 'ScienceDirect'
    allowed_domains = ['https://www.sciencedirect.com/']
    start_urls = ['http://https://www.sciencedirect.com//']

    def parse(self, response):
        pass
