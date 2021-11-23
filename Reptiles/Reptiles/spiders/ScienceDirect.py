import scrapy
from Reptiles.items import ReptilesItem
import urllib
import json
import logging
import re

class SciencedirectSpider(scrapy.Spider):
    name = 'ScienceDirect'
    allowed_domains = ['www.sciencedirect.com']
    start_urls = ['https://www.sciencedirect.com/search?date=2020']

    def __init__(self):
        super(SciencedirectSpider, self).__init__()

    def parse(self, response):
        # f1 = open('test.html', 'w')
        # f1.write(response.text)
        # f1.close()
        logging.info('parse ' + response.url)
        for page in range(1, 46, 1):
            next_url = 'https://www.sciencedirect.com/browse/journals-and-books?contentType=JL&page=' + str(page)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_venue_list,
            )
            break


    def parse_venue_list(self, response):
        logging.info('parse_venue_list ' + response.url)
        venues = response.xpath('//li[@class="publication branded u-padding-xs-ver js-publication"]/a/span/text()')
        for venue in venues:
            venue = venue.extract()
            for date in range(1995, 2022, 1):
                next_url = 'https://www.sciencedirect.com/search?date=' + str(date) + "&pub=" + str(venue) + "&show=100&offset=" + str(self.offset)
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_token,
                )
            break
        break
    
    def parse_token(self, response):
        logging.info('parse_token ' + response.url)
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
        
        next_url = re.sub('https://www.sciencedirect.com/search', 'https://www.sciencedirect.com/search/api', response.url) + '&t=' + token
        yield scrapy.Request(
            url=next_url,
            callback=self.parse_paper_list,
        )

    def parse_paper_list(self, response):
        logging.info('parse_paper_list ' + response.url)
        results = json.loads(response.text)
        for paper_item in results['searchResults']:
            link = paper_item['link']
            next_url = urllib.parse.urljoin("https://www.sciencedirect.com/", link)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_read,
            )
            break
        resultsFound = 0
        for paper_item in scripts:
            tmpstr = re.search('"resultsFound":"[0-9]*"', paper_item.extract())
            if tmpstr is not None:
                tmpstr = tmpstr.group()
                resultsFound = tmpstr[15:-1]
                break
        print('resultsFound', resultsFound)
        raise NotImplemented
        # if len(results['searchResults']) > 0:
        #     self.offset += len(results['searchResults'])
        #     next_url = re.sub("&offset=.&", "&offset=" + str(self.offset) + "&", response.url)
        #     yield scrapy.Request(
        #         url=next_url,
        #         callback=self.parse_paper_list,
        #     )

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
                meta={'item':item}
            )
    
    def parse_read1(self, response):
        # inCitations
        logging.info('parse_read1 ' + response.url)
        item = response.meta['item']
        results = json.loads(response.text)
        item['inCitations'] = str(results['hitCount'])
        # print('item', item)
        yield item

