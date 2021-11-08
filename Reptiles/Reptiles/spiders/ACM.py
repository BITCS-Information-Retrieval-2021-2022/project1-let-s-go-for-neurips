import scrapy
from Reptiles.items import ReptilesItem
from scrapy.utils.project import get_project_settings
import logging
import re
import datetime
# from acaSpider.proxyDownloader import getProxy



class AcmSpider(scrapy.Spider):
    name = 'ACM'
    allowed_domains = ['dl.acm.org/']
    start_urls = get_project_settings().get('ACM_URL')


    def __init__(self):
        super(AcmSpider, self).__init__()
        self.startPage = 0
        self.pageSize = 20
        self.startTime = get_project_settings().get('START_TIME')
        # self.proxyUpdateDelay = get_project_settings().get('PROXY_UPDATE_DELAY')
        # getProxy().main()

    def parse(self, response):
        paper_items = response.xpath('//span[@class="hlFld-Title"]/a/@href')
        results_num = response.xpath('//span[@class="hitsLength"]/text()').extract()[0].replace(',', '')
        
        for paper_item in paper_items:
            print(paper_item)
            logging.warning("This is a Href",paper_item)


        if (self.startPage + 1) * self.pageSize < int(results_num) and self.startPage < 1:
            self.startPage += 1
            next_url = self.start_urls[0] + '&startPage=' + str(self.startPage) + '&pageSize=' + str(self.pageSize)
            yield scrapy.Request(
                next_url,
                callback=self.parse,
            )