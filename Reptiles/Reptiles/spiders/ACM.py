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
        item = ReptilesItem()
    #     print('爬取第', self.startPage, '页')

    #     results_num = response.xpath('//span[@class="hitsLength"]/text()').extract()[0].replace(',', '')
    #     subjects = response.xpath('//ul[@class="rlist--inline facet__list--applied"]/li/span/text()').extract()[0]
    #     response = response.xpath('//li[@class="search__item issue-item-container"]')

       
    #     logging.warning('$ ACM_Spider已爬取：' + str((self.startPage + 1) * self.pageSize))

    #     if (datetime.datetime.now() - self.startTime).seconds > self.proxyUpdateDelay:
    #         # getProxy().main()
    #         print('已爬取：', (self.startPage + 1) * self.pageSize)
    #         logging.warning('$ ACM_Spider runs getProxy')

    #     if (self.startPage + 1) * self.pageSize < int(results_num) and self.startPage < 1:
    #         self.startPage += 1
    #         next_url = self.start_urls[0] + '&startPage=' + str(self.startPage) + '&pageSize=' + str(self.pageSize)
    #         yield scrapy.Request(
    #             next_url,
    #             callback=self.parse,
    #         )

    # def remove_html(self, string):
    #     pattern = re.compile(r'<[^>]+>')
    #     return (re.sub(pattern, '', string).replace('\n', '').replace('  ', '')).strip()

    # def remove4year(self, string):
    #     return string.split(', ')[0]

    # def merge_authors(self, au_list):
    #     au_str = ''
    #     for i in au_list:
    #         au_str += i + ','
    #     return au_str.strip(',')

