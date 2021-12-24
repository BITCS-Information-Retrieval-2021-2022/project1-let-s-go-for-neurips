import scrapy
from Reptiles.items import ReptilesItem
import urllib
import json
import logging
import re
import pymongo

wordtonumber = {
    'January': '1',
    'February': '2',
    'March': '3',
    'April': '4',
    'May': '5',
    'June': '6',
    'July': '7',
    'August': '8',
    'September': '9',
    'October': '10',
    'November': '11',
    'December': '12',
}


class SciencedirectSpider(scrapy.Spider):
    name = 'ScienceDirect'
    allowed_domains = ['www.sciencedirect.com']
    start_urls = ['https://www.sciencedirect.com/search?date=2020']

    def __init__(self):
        super(SciencedirectSpider, self).__init__()
        with open('venue_cid', 'r') as f:
            self.venue_list = f.readlines()
        self.client = pymongo.MongoClient(
            host='127.0.0.1', port=27017, tz_aware=True)
        self.db = self.client.pc
        self.docs = self.db.get_collection("Process")
        self.title = 'ScienceDirect'
        self.config = self.docs.find_one({'title': self.title})

    def start_requests(self):
        logging.info('start_requests')
        venue_id = int(self.config['venue_id'])
        year = int(self.config['year'])

        next_url = 'https://www.sciencedirect.com/search?date=' + str(year) + "&cid=" \
            + str(self.venue_list[venue_id]) + "&show=100&offset=0"
        yield scrapy.Request(
            url=next_url,
            callback=self.parse,
            meta={
                'year': year,
                'venue_id': venue_id,
            }
        )

    def parse(self, response):
        logging.info('parse ' + response.url)
        pre_meta = response.request.meta
        year = int(pre_meta['year'])
        venue_id = int(pre_meta['venue_id'])
        self.update_process(year, venue_id)
        scripts = response.xpath('//script')
        token = ''
        for paper_item in scripts:
            tmpstr = re.search(
                '"searchToken":"([a-zA-Z0-9]|\\%)*"', paper_item.extract())
            if tmpstr is not None:
                tmpstr = tmpstr.group()
                token = tmpstr[15:-1]
                break
        if token == '':
            logging.error('not find token ' + response.url)
        else:
            next_url = re.sub('https://www.sciencedirect.com/search',
                              'https://www.sciencedirect.com/search/api', response.url) + '&t=' + token
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_paper_list,
                meta={
                    'year': pre_meta['year'],
                    'venue_id': pre_meta['venue_id'],
                    'doneflag': False,
                }
            )

    def parse_paper_list(self, response):
        logging.info('parse_paper_list ' + response.url)
        pre_meta = response.request.meta
        year = int(pre_meta['year'])
        venue_id = int(pre_meta['venue_id'])
        results = json.loads(response.text)
        pre_meta = response.request.meta
        if 'searchResults' in results:
            for paper_item in results['searchResults']:
                link = paper_item['link']
                next_url = urllib.parse.urljoin(
                    "https://www.sciencedirect.com/", link)
                doneflag = pre_meta['doneflag']
                if doneflag and paper_item == results['searchResults'][-1]:
                    doneflag = True
                else:
                    doneflag = False
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_read,
                    meta={
                        'year': year,
                        'venue_id': venue_id,
                        'doneflag': doneflag,
                    }
                )

        flag = False
        if 'resultsFound' in results and int(results['resultsFound']) > 0:
            resultsFound = int(results['resultsFound'])
            offset = int(re.search('offset=[0-9]*', response.url).group()[7:])
            if resultsFound > offset + 100 and offset < 900:
                offset += 100
                next_url = re.sub(
                    "&offset=[0-9]*", "&offset=" + str(offset), response.url)
                if offset == 900 or resultsFound <= offset + 100:
                    doneflag = True
                else:
                    doneflag = False
                flag = True
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_paper_list,
                    meta={
                        'year': year,
                        'venue_id': venue_id,
                        'doneflag': doneflag,
                    }
                )
        if not flag:
            logging.info('----done2---- year ' + str(year)
                         + ' venue_id ' + str(venue_id))
            venue_id += 1
            if venue_id == len(self.venue_list):
                year -= 1
                venue_id = 0
            if year >= 2000:
                next_url = 'https://www.sciencedirect.com/search?date=' + \
                    str(year) + "&cid=" + \
                    str(self.venue_list[venue_id]) + "&show=100&offset=0"
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={
                        'year': year,
                        'venue_id': venue_id,
                    }
                )

    def parse_read(self, response):
        # f1 = open('test.html', 'w')
        # f1.write(response.text)
        # f1.close()
        pre_meta = response.request.meta
        year = int(pre_meta['year'])
        venue_id = int(pre_meta['venue_id'])
        doneflag = pre_meta['doneflag']
        logging.info('parse_read ' + response.url)
        item = ReptilesItem()
        item['title'] = response.xpath(
            '//meta[@name="citation_title"]/@content').extract()[0]
        item['abstract'] = response.xpath(
            'normalize-space(//div[@class="abstract author"]/div/p)').extract()[0]
        given_name = response.xpath(
            '//a[@class="author size-m workspace-trigger"]/span/span[@class="text given-name"]/text()').extract()
        surname = response.xpath(
            '//a[@class="author size-m workspace-trigger"]/span/span[@class="text surname"]/text()').extract()
        item['authors'] = [name1 + ' ' + name2 for name1,
                           name2 in zip(given_name, surname)]
        item['doi'] = response.xpath(
            '//div[@class="ArticleIdentifierLinks"]/a[@class="doi"]/@href').extract()[0]
        item['url'] = response.url
        scripts = response.xpath('//script')
        month = ''
        year = ''
        for paper_item in scripts:
            tmpstr = re.search(
                '"Publication date":"([a-zA-Z0-9]| )*"', paper_item.extract())
            if tmpstr is not None:
                tmpstr = tmpstr.group()
                month = re.split(' ', tmpstr)[-2]
                year = re.split(' ', tmpstr)[-1][:-1]
                break
        item['month'] = wordtonumber[month]
        item['year'] = year
        paper_type = ''
        for paper_item in scripts:
            tmpstr = re.search(
                '"publicationType":"([a-zA-Z])*"', paper_item.extract())
            if tmpstr is not None:
                tmpstr = tmpstr.group()
                paper_type = tmpstr[19:-1]
                break
        item['type'] = paper_type
        item['venue'] = response.xpath(
            '//img[@class="publication-cover-image"]/@alt').extract()[0]
        item['source'] = "Elsevier"
        item['video_url'] = ''
        item['video_path'] = ''
        item['thumbnail_url'] = ''
        outCitations = ''
        for paper_item in scripts:
            tmpstr = re.search(
                '"document-references":[0-9]*', paper_item.extract())
            if tmpstr is not None:
                tmpstr = tmpstr.group()
                outCitations = str(tmpstr[22:])
                break
        item['outCitations'] = outCitations
        item['pdf_url'] = item['url'] + '/pdfft'
        # item['pdf_path'] = './PDF/ScienceDirect/' + re.sub(r'[^\w\s]', '', item['title']).lower().replace(' ','_')+'.pdf'
        item['pdf_path'] = ''
        pii = re.split('/', response.url)[-1]
        next_url = 'https://www.sciencedirect.com/sdfe/arp/pii/' + pii + '/citingArticles'

        yield scrapy.Request(
            url=next_url,
            callback=self.parse_read1,
            meta={
                'item': item,
                'year': year,
                'venue_id': venue_id,
                'doneflag': doneflag,
            }
        )

    def parse_read1(self, response):
        # inCitations
        logging.info('parse_read1 ' + response.url)
        pre_meta = response.request.meta
        year = int(pre_meta['year'])
        venue_id = int(pre_meta['venue_id'])
        doneflag = pre_meta['doneflag']
        item = response.meta['item']
        results = json.loads(response.text)
        item['inCitations'] = str(results['hitCount'])
        yield item

        if doneflag:
            logging.info('----done1---- year ' + str(year)
                         + ' venue_id ' + str(venue_id))
            venue_id += 1
            if venue_id == len(self.venue_list):
                year -= 1
                venue_id = 0
            if year >= 2000:
                next_url = 'https://www.sciencedirect.com/search?date=' + \
                    str(year) + "&cid=" + \
                    str(self.venue_list[venue_id]) + "&show=100&offset=0"
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    meta={
                        'year': year,
                        'venue_id': venue_id,
                    }
                )

    def update_process(self, year, venue_id):
        process = {
            'year': year,
            'venue_id': venue_id,
        }
        logging.info('----update_process---- year '
                     + str(year) + ' venue_id ' + str(venue_id))
        self.docs.update({'title': self.title}, {'$set': process}, True)
