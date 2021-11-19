import scrapy
from Reptiles.items import ReptilesItem
import urllib
from scrapy.utils.project import get_project_settings
import logging
import re
import datetime


class SpringerSpider(scrapy.Spider):
    name = 'Springer'
    allowed_domains = ['link.springer.com']
    start_urls = ['https://link.springer.com/search/page/1']

    def __init__(self):
        super(SpringerSpider, self).__init__()
        self.startPage = 1
        self.pageSize = 20
        self.startTime = get_project_settings().get('START_TIME')
        # self.proxyUpdateDelay = get_project_settings().get('PROXY_UPDATE_DELAY')
        # getProxy().main()

    def parse(self, response):
        paper_items = response.xpath('//a[@class="title"]/@href')
        results_num = response.xpath('//strong/text()').extract()[0].replace(',', '')

        # yield scrapy.Request(
        #     url='https://link.springer.com/referenceworkentry/10.1007/978-3-319-89999-2_172',
        #     callback=self.readChapter,
        # )

        for paper_item in paper_items:
            paper_type = str(re.search(r'/(.*?)/', paper_item.extract()).group(0))
            if(paper_type == '/article/'):
                # print(paper_item.extract())
                next_url = urllib.parse.urljoin("https://link.springer.com/", paper_item.extract())
                yield scrapy.Request(
                    url=next_url,
                    callback=self.readArticle,
                )
            if (paper_type == '/chapter/' or paper_type == '/protocol/'):
                # print(paper_item.extract())
                next_url = urllib.parse.urljoin("https://link.springer.com/", paper_item.extract())
                yield scrapy.Request(
                    url=next_url,
                    callback=self.readChapter,
                )
            if (paper_type == '/referenceworkentry/'):
                # print(paper_item.extract())
                next_url = urllib.parse.urljoin("https://link.springer.com/", paper_item.extract())
                yield scrapy.Request(
                    url=next_url,
                    callback=self.readReferenceworkentry,
                )

        # if (self.startPage + 1) * self.pageSize < int(results_num):
        #     self.startPage += 1
        #     next_url = self.start_urls[0][:-1] + str(self.startPage)
        #     print("——————翻页————————")
        #     yield scrapy.Request(
        #         next_url,
        #         callback=self.parse,
        #     )

    def readArticle(self, response):
        item = ReptilesItem()
        # 论文主页
        item['title'] = response.xpath('//h1[@class="c-article-title"]/text()').extract()
        item['authors'] = response.xpath('//a[@data-test="author-name"]/text()').extract()
        item['abstract'] = response.xpath('//*[@id="Abs1-content"]/p/text()').extract()
        item['venue'] = response.xpath('//a[@data-test="journal-link"]/i/text()').extract()
        # 论文主页
        item['url'] = response.xpath('//span[@class="c-bibliographic-information__value"]/a/text()').extract()
        item['doi'] = response.xpath('//span[@class="c-bibliographic-information__value"]/a/text()').extract()
        # 数据源
        item['source'] = ['Springer']
        # 视频链接：无
        # item['video_url'] = []
        # video_url = response.xpath('//div[@class="video__links table__cell-view"]/a/@href').extract()
        # for url in video_url:
        #     if url is '#':
        #         pass
        #     else:
        #         url_complete = 'https://dl.acm.org' + url
        #         item['video_url'].append(url_complete)
        # 发表年月
        type = response.xpath('//li[@class="c-bibliographic-information__list-item"]/p/text()').extract()
        date = response.xpath('//span[@class="c-bibliographic-information__value"]/time/text()').extract()
        for i in range(len(type)):
            if(type[i] == 'Published'):
                publishx = date[i].split(' ')
                item['year'] = [publishx[2]]
                item['month'] = [publishx[1]]
        # 论文type：无
        # pdf链接
        item['pdf_url'] = response.xpath('//div[@class="c-pdf-download u-clear-both"]/a/@href')[0].extract()
        # 该论文被引用的数量：无
        # item['inCitations'] = [response.xpath('//span[@class="citation"]/span/text()')[0].extract()]
        item['outCitations'] = response.xpath('//span[@class="c-article-references__counter"]/text()')[-1].extract()
        print(item)
        yield item

    def readChapter(self, response):
        item = ReptilesItem()
        # 论文主页
        item['title'] = response.xpath('//h1[@class="ChapterTitle"]/text()').extract()
        item['authors'] = response.xpath('//span[@class="authors__name"]/text()').extract()
        for i in range(len(item['authors'])):
            item['authors'][i] = item['authors'][i].replace("\xa0", " ")
        item['abstract'] = response.xpath('//p[@class="Para"]/text()').extract()
        item['venue'] = response.xpath('//span[@data-test="ConfSeriesName"]/text()').extract()
        # 论文主页
        item['url'] = response.xpath('//span[@id="doi-url"]/text()').extract()
        item['doi'] = response.xpath('//span[@id="doi-url"]/text()').extract()
        # 数据源
        item['source'] = ['Springer']
        # 视频链接：无
        # item['video_url'] = []
        # video_url = response.xpath('//div[@class="video__links table__cell-view"]/a/@href').extract()
        # for url in video_url:
        #     if url is '#':
        #         pass
        #     else:
        #         url_complete = 'https://dl.acm.org' + url
        #         item['video_url'].append(url_complete)
        # 发表年月
        publish = response.xpath('//span[@class="bibliographic-information__value u-overflow-wrap"]/text()').extract()
        publishx = publish[0].split(' ')
        item['year'] = [publishx[2]]
        item['month'] = [publishx[1]]
        # 论文type
        item['type'] = response.xpath('//span[@class="test-render-category"]/text()').extract()
        # pdf链接：无
        #item['pdf_url'] = response.xpath('//*[@id="cobranding-and-download-availability-text"]/div/a/@href').extract()
        # 该论文被引用的数量：无
        # item['inCitations'] = [response.xpath('//span[@class="citation"]/span/text()')[0].extract()]
        item['outCitations'] = response.xpath('//div[@class="CitationNumber"]/text()')[-1].extract()
        yield item

    def readReferenceworkentry(self, response):
        item = ReptilesItem()
        # 论文主页
        item['title'] = response.xpath('//h1[@class="ChapterTitle"]/text()').extract()
        item['authors'] = response.xpath('//span[@class="authors__name"]/text()').extract()
        for i in range(len(item['authors'])):
            item['authors'][i] = item['authors'][i].replace("\xa0", " ")
        item['abstract'] = response.xpath('//p[@class="Para"]/text()').extract()
        item['venue'] = response.xpath('//span[@data-test="ConfSeriesName"]/text()').extract()
        # 论文主页
        item['url'] = response.xpath('//span[@id="doi-url"]/text()').extract()
        item['doi'] = response.xpath('//span[@id="doi-url"]/text()').extract()
        # 数据源
        item['source'] = ['Springer']
        # 视频链接：无
        # item['video_url'] = []
        # video_url = response.xpath('//div[@class="video__links table__cell-view"]/a/@href').extract()
        # for url in video_url:
        #     if url is '#':
        #         pass
        #     else:
        #         url_complete = 'https://dl.acm.org' + url
        #         item['video_url'].append(url_complete)
        # 发表年月
        publish = response.xpath('//span[@class="bibliographic-information__value u-overflow-wrap"]/text()').extract()
        publishx = publish[0].split(' ')
        item['year'] = [publishx[2]]
        item['month'] = [publishx[1]]
        # 论文type
        item['type'] = response.xpath('//span[@class="test-render-category"]/text()').extract()
        # pdf链接：无
        #item['pdf_url'] = response.xpath('//*[@id="cobranding-and-download-availability-text"]/div/a/@href').extract()
        # 该论文被引用的数量：无
        # item['inCitations'] = [response.xpath('//span[@class="citation"]/span/text()')[0].extract()]
        # item['outCitations'] = response.xpath('//div[@class="CitationNumber"]/text()')[-1].extract()
        item['outCitations'] = response.xpath('//div[@class="CitationContent"]/@id')[-1].extract()
        item['outCitations'] = item['outCitations'][2:]
        yield item