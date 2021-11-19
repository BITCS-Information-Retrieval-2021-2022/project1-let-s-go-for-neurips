import scrapy
from Reptiles.items import ReptilesItem
import urllib
import json
import logging
import re

class SciencedirectSpider(scrapy.Spider):
    name = 'ScienceDirect'
    allowed_domains = ['www.sciencedirect.com']
    # start_urls = ['https://www.sciencedirect.com/search/api?date=2021&offset=0&t=a8NiX7cJ6Qjx6Ozy%252FMF7xdJCd4wsZKGrg1Kz0n3mskmaa%252F8but7D8hb5%252FOlDboRY3jly8Pxl8wHpgRGwuh72ffyEBYpstp27OHDv1eT9n3DAQzsTjPv7ev%252B2vDpH%252BN1MvKdDbfVcomCzYflUlyb3MA%253D%253D&hostname=www.sciencedirect.com']
    start_urls = ['https://www.sciencedirect.com/search?date=2020']

    def __init__(self):
        super(SciencedirectSpider, self).__init__()
        self.search_api = 'https://www.sciencedirect.com/search/api?'
        self.date = 2020
        self.offset = 0
        self.hostname = 'www.sciencedirect.com'

    def parse(self, response):
        # f1 = open('test.html', 'w')
        # f1.write(response.text)
        # f1.close()
        logging.info('parse ' + response.url)
        scripts = response.xpath('//script')
        token = ''
        for paper_item in scripts:
            tmpstr = re.search('"searchToken":"([a-zA-Z0-9]|\%)*"', paper_item.extract())
            if tmpstr is not None:
                tmpstr = tmpstr.group()
                token = tmpstr[15:-1]
                break
        if token == '':
            logging.error('not find token ' + response.url)

        next_url = self.search_api + "date=" + str(self.date) + "&show=100&offset=" + str(self.offset) + "&t=" + str(token) + "&hostname=" + str(self.hostname)
        yield scrapy.Request(
            url=next_url,
            callback=self.parse_list,
        )



    def parse_list(self, response):
        logging.info('parse_list ' + response.url)
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
                callback=self.parse_list,
            )

    def parse_read(self, response):
        # f1 = open('test.html', 'w')
        # f1.write(response.text)
        # f1.close()
        logging.info('parse_read ' + response.url)
        item = ReptilesItem()
        item['title'] = response.xpath('//meta[@name="citation_title"]/@content').extract()[0]#titleString|citation_title|title
        item['abstract'] = response.xpath('normalize-space(//div[@class="abstract author"]/div/p)').extract()[0]#abstracts
        given_name = response.xpath('//a[@class="author size-m workspace-trigger"]/span/span[@class="text given-name"]/text()').extract()
        surname = response.xpath('//a[@class="author size-m workspace-trigger"]/span/span[@class="text surname"]/text()').extract()
        item['authors'] = [name1 + ' ' + name2 for name1, name2 in zip(given_name, surname)]
        item['doi'] = response.xpath('//div[@class="ArticleIdentifierLinks"]/a[@class="doi"]/@href').extract()[0]
        item['url'] = response.url
        scripts = response.xpath('//script')
        month = ''
        year = ''
        for paper_item in scripts:
            tmpstr = re.search('"Publication date":"([a-zA-Z0-9]| )*"', paper_item.extract())
            if tmpstr is not None:
                tmpstr = tmpstr.group()#cover-date-text|Publication date
                month = re.split(' ', tmpstr)[-2]
                year = re.split(' ', tmpstr)[-1][:-1]
                break
        item['month'] = month
        item['year'] = year
        paper_type = ''
        for paper_item in scripts:
            tmpstr = re.search('"publicationType":"([a-zA-Z])*"', paper_item.extract())
            if tmpstr is not None:
                tmpstr = tmpstr.group()
                paper_type = tmpstr[19:-1]
                break
        item['type'] = paper_type
        item['venue'] = response.xpath('//img[@class="publication-cover-image"]/@alt').extract()[0]
        item['source'] = "Elsevier"
        item['video_url'] = ''
        item['video_path'] = ''
        item['thumbnail_url'] = ''
        outCitations = ''
        for paper_item in scripts:
            tmpstr = re.search('"document-references":[0-9]*', paper_item.extract())
            if tmpstr is not None:
                tmpstr = tmpstr.group()
                outCitations = str(tmpstr[22:])
                break
        item['outCitations'] = outCitations
        pdf_url = ''
        for paper_item in scripts:
            tmpstr = re.search('"md5":"[a-zA-Z0-9]*"', paper_item.extract())
            if tmpstr is not None:
                md5 = tmpstr.group()[7:-1]
                tmpstr = re.search('"pid":"([a-zA-Z0-9]|\-|\.)*.pdf"', paper_item.extract())
                pid = tmpstr.group()[7:-1]
                pdf_url = response.url + '/pdf?md5=' + md5 + '&pid=' + pid
                break
        item['pdf_url'] = pdf_url
        pii = re.split('/', response.url)[-1]
        next_url = 'https://www.sciencedirect.com/sdfe/arp/pii/' + pii + '/citingArticles?creditCardPurchaseAllowed=true&preventTransactionalAccess=false&preventDocumentDelivery=true'

        yield scrapy.Request(
                url=next_url,
                callback=self.parse_read1,
                meta={
                    'item':item,
                }
            )
    
    def parse_read1(self, response):
        # inCitations
        logging.info('parse_read1 ' + response.url)
        item = response.meta['item']
        results = json.loads(response.text)
        item['inCitations'] = str(results['hitCount'])
        # print('item', item)
        yield item

