import scrapy
from Reptiles.items import ReptilesItem
import urllib
from scrapy.utils.project import get_project_settings
import logging
import re
import datetime
# from acaSpider.proxyDownloader import getProxy



class AcmSpider(scrapy.Spider):
    name = 'ACM'
    allowed_domains = ['dl.acm.org']
    start_urls = get_project_settings().get('ACM_URL')

    def __init__(self):
        super(AcmSpider, self).__init__()
        self.startPage = 0
        self.pageSize = 20
        self.ID = 777
        self.startTime = get_project_settings().get('START_TIME')
        # self.proxyUpdateDelay = get_project_settings().get('PROXY_UPDATE_DELAY')
        # getProxy().main()

    def parse(self, response):
        print(response.url)
        paper_items = response.xpath('//span[@class="hlFld-Title"]/a/@href')
        results_num = response.xpath('//span[@class="hitsLength"]/text()').extract()[0].replace(',', '')
        for paper_item in paper_items:
            logging.warning("密码")
            next_url = urllib.parse.urljoin("https://dl.acm.org/", paper_item.extract())
            yield scrapy.Request(
                url=next_url,
                callback=self.read,
            )

        if (self.startPage + 1) * self.pageSize < int(results_num):
            self.startPage += 1
            next_url = self.start_urls[0][:-3] + str(self.ID) + '&startPage=' + str(self.startPage) + '&pageSize=' + str(self.pageSize)
            print("——————翻页————————")
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
            )
        else:
            self.startPage = 0
            self.ID += 1
            print("——————修改路径ID——————")
            next_url = self.start_urls[0][:-3] + str(self.ID)
            # print(next_url)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
            )

    def read(self, response):
        item = ReptilesItem()
        # 论文主页
        item['title'] = response.xpath('//h1[@class="citation__title"]/text()').extract()
        item['authors'] = response.xpath('//span[@class="loa__author-name"]/span/text()').extract()
        item['abstract'] = response.xpath('//div[@class="abstractSection abstractInFull"]/p/text()').extract()
        item['venue'] = response.xpath('//span[@class="epub-section__title"]/text()').extract()
        # 论文主页
        item['url'] = response.xpath('//span[@class="dot-separator"]/a/@href').extract()
        item['doi'] = response.xpath('//span[@class="dot-separator"]/a/@href').extract()
        #数据源
        item['source'] = ['ACM']
        # 视频链接
        item['video_url'] = []
        video_url = response.xpath('//div[@class="video__links table__cell-view"]/a/@href').extract()
        for url in video_url:
            if url is '#':
                pass
            else:
                url_complete = 'https://dl.acm.org'+url
                item['video_url'].append(url_complete)
        # 发表年月
        publish = response.xpath('//span[@class="CitationCoverDate"]/text()').extract()
        publishx = publish[0].split(' ')
        item['year'] = [publishx[2]]
        item['month'] = [publishx[1]]
        # pdf链接：无
        # 该论文被引用的数量
        item['inCitations'] = [response.xpath('//span[@class="citation"]/span/text()')[0].extract()]
        print(item['url'])
        yield item