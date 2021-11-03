import scrapy


class SpringerSpider(scrapy.Spider):
    name = 'Springer'
    allowed_domains = ['https://www.springer.com/cn']
    start_urls = ['http://https://www.springer.com/cn/']

    def parse(self, response):
        pass
