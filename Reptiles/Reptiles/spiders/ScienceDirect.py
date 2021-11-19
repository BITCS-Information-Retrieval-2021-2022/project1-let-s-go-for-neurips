import scrapy
from Reptiles.items import ReptilesItem
import urllib
import json
import re

class SciencedirectSpider(scrapy.Spider):
    name = 'ScienceDirect'
    allowed_domains = ['www.sciencedirect.com']
    # start_urls = ['https://www.sciencedirect.com/search/api?date=2021&offset=0&t=a8NiX7cJ6Qjx6Ozy%252FMF7xdJCd4wsZKGrg1Kz0n3mskmaa%252F8but7D8hb5%252FOlDboRY3jly8Pxl8wHpgRGwuh72ffyEBYpstp27OHDv1eT9n3DAQzsTjPv7ev%252B2vDpH%252BN1MvKdDbfVcomCzYflUlyb3MA%253D%253D&hostname=www.sciencedirect.com']
    start_urls = ['https://www.sciencedirect.com/search?date=2020']

    def __init__(self):
        super(SciencedirectSpider, self).__init__()
        self.search_api = 'https://www.sciencedirect.com/search/api?'
        self.date = 2010
        self.offset = 0
        self.hostname = 'www.sciencedirect.com'

    def parse(self, response):
        # f1 = open('test.html', 'w')
        # f1.write(response.text)
        # f1.close()

        print('parse', response.url)
        scripts = response.xpath('//script')
        for paper_item in scripts:
            tokenstr = re.findall('"searchToken":.*"}', paper_item.extract())
            if len(tokenstr) > 0:
                token = tokenstr[0][15:-2]
                break

        next_url = self.search_api + "date=" + str(self.date) + "&offset=" + str(self.offset) + "&t=" + str(token) + "&hostname=" + str(self.hostname)
        yield scrapy.Request(
            url=next_url,
            callback=self.parse_js,
        )



    def parse_js(self, response):
        print('parse_js', response.url)
        results = json.loads(response.text)
        for paper_item in results['searchResults']:
            link = paper_item['link']
            next_url = urllib.parse.urljoin("https://www.sciencedirect.com/", link)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_read,
            )
        if len(results['searchResults']) > 0:
            self.offset += len(results['searchResults'])
            next_url = re.sub("&offset=.&", "&offset=" + str(self.offset) + "&", response.url)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_js,
            )

    def parse_read(self, response):
        # f1 = open('test.html', 'w')
        # f1.write(response.text)
        # f1.close()

        print('parse_read', response.url)
        item = ReptilesItem()
        item['title'] = response.xpath('normalize-space(//span[@class="title-text"]/text())').extract()[0]#todo \n
        item['abstract'] = response.xpath('normalize-space(//div[@class="abstract author"]/div/p)').extract()[0]#todo \n
        given_name = response.xpath('//a[@class="author size-m workspace-trigger"]/span/span[@class="text given-name"]/text()').extract()
        surname = response.xpath('//a[@class="author size-m workspace-trigger"]/span/span[@class="text surname"]/text()').extract()
        item['authors'] = [name1 + ' ' + name2 for name1, name2 in zip(given_name, surname)]
        item['doi'] = response.xpath('//div[@class="ArticleIdentifierLinks"]/a[@class="doi"]/@href').extract()[0]
        item['url'] = response.url
        time = re.findall('<!--\s-->.*\s.*\s.*<!--\s-->', response.xpath('//div[@class="publication-brand"]/div').extract()[0])[0][8:-8]
        item['year'] = time[-4:]
        item['month'] = re.findall('\s.*\s', time)[0][1:-1]
        item['type'] = None#todo find
        item['venue'] = response.xpath('//img[@class="publication-cover-image"]/@alt').extract()[0]
        item['source'] = "Elsevier"
        item['video_url'] = None
        item['video_path'] = None
        item['thumbnail_url'] = None
        item['pdf_url'] = response.xpath('//a[@class="link-button link-button-primary accessbar-primary-link"]/@href').extract()#todo AJAX
        item['pdf_path'] = None
        item['inCitations'] = response.xpath('//header[@id="citing-articles-header"]/button/span').extract()#todo AJAX
        item['outCitations'] = response.xpath('//dl[@class="references"]/dd[@class="reference"]')#todo AJAX
        # print('item', item)
        yield item
