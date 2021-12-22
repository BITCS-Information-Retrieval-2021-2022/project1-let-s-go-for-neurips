import scrapy
from Reptiles.items import ReptilesItem
import urllib
from scrapy.utils.project import get_project_settings
import logging
import re
import datetime
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


class SpringerSpider(scrapy.Spider):
    name = 'Springer'
    allowed_domains = ['link.springer.com']
    start_urls = ['https://link.springer.com/search/page/1?facet-content-type=%22Journal%22']

    def __init__(self):
        super(SpringerSpider, self).__init__()
        self.startPage = 1
        self.pageSize = 20
        self.startTime = get_project_settings()\
            .get('START_TIME')
        # self.proxyUpdateDelay =
        # get_project_settings().get('PROXY_UPDATE_DELAY')
        # getProxy().main()
        self.url = 'https://link.springer.com/search/page/{}?facet-content-type=%22{}%22'

        self.client = pymongo.MongoClient(host='10.1.114.77', port=27017, tz_aware=True)
        self.db = self.client.pc
        self.docs = self.db.get_collection("Process")
        self.config = self.docs.find_one({'title': 'Springer'})
        print(self.config)

    def parse(self, response):
        type = self.config['type']
        page = self.config['page']
        next_url = self.url.format(page, type)
        self.startPage = page
        if type == 'Journal':
            yield scrapy.Request(
                url=next_url,
                callback=self.parse1,
            )
        if type == 'ConferenceProceedings':
            yield scrapy.Request(
                url=next_url,
                callback=self.parse2,
            )

    def parse1(self, response):
        journal_items = response.xpath('//a[@class="title"]/@href')
        # results_num = response.xpath('//strong/text()').extract()[0].replace(',', '')
        page_num = int(response.xpath('//span[@class="number-of-pages"]/text()').extract()[0].replace(',', ''))
        # print(journal_items)
        # print(page_num)

        # yield scrapy.Request(
        #     url='https://link.springer.com/referenceworkentry/10.1007/978-3-319-89999-2_172',
        #     callback=self.readChapter,
        # )

        for journal_item in journal_items:
            journal_num = str(journal_item.extract()).replace(str(re.search(r'/(.*?)/', journal_item.extract()).group(0)), "")
            next_url = 'https://link.springer.com/search/page/1?search-within=Journal&facet-journal-id=' \
                       + journal_num + '&query='
            # print(next_url)
            yield scrapy.Request(
                url=next_url,
                callback=self.parseJournal,
                meta={'journal_num': journal_num},
            )
            # next_url = urllib.parse.urljoin("https://link.springer.com/", paper_item.extract())
            # yield scrapy.Request(
            #     url=next_url,
            #     callback=self.readArticle,
            # )

        self.update_process('Journal', self.startPage + 1)
        logging.info("Journal{}页爬取完毕".format(self.startPage))

        if self.startPage < page_num:
            self.startPage += 1
            next_url = 'https://link.springer.com/search/page/' + str(self.startPage) + '?facet-content-type=%22Journal%22'
            # print("——————翻页————————")
            yield scrapy.Request(
                next_url,
                callback=self.parse1,
            )
        else:
            next_url = 'https://link.springer.com/search/page/1?facet-content-type=%22ConferenceProceedings%22'
            self.startPage = 1
            yield scrapy.Request(
                url=next_url,
                callback=self.parse2,
            )

    def parse2(self, response):
        chapter_items = response.xpath('//a[@class="title"]/@href')
        # results_num = response.xpath('//strong/text()').extract()[0].replace(',', '')
        page_num = int(response.xpath('//span[@class="number-of-pages"]/text()').extract()[0].replace(',', ''))
        # print(chapter_items)
        # print(page_num)

        for chapter_item in chapter_items:
            chapter_num = str(chapter_item.extract()).replace(str(re.search(r'/(.*)/', chapter_item.extract()).group(0)), "")
            next_url = 'https://link.springer.com/search/page/1?facet-content-type=Chapter&query=&facet-eisbn=' + chapter_num
            # print(next_url)
            yield scrapy.Request(
                url=next_url,
                callback=self.parseChapter,
                meta={'chapter_num': chapter_num},
            )

        self.update_process('ConferenceProceedings', self.startPage + 1)
        logging.info("ConferenceProceedings{}页爬取完毕".format(self.startPage))

        if self.startPage < page_num:
            self.startPage += 1
            next_url = 'https://link.springer.com/search/page/' + str(self.startPage) + \
                       '?facet-content-type=%22ConferenceProceedings%22'
            # print("——————翻页————————")
            yield scrapy.Request(
                next_url,
                callback=self.parse2,
            )

    def parseJournal(self, response):
        journal_page = 1
        page_num = int(response.xpath('//span[@class="number-of-pages"]/text()').extract()[0].replace(',', ''))
        journal_num = response.meta['journal_num']

        for journal_page in range(1, page_num + 1):
            # logging.info("——————————————————开始从{}期刊{}页爬取——————————————————".format(journal_num, journal_page))
            next_url = 'https://link.springer.com/search/page/' + str(journal_page) + \
                       '?search-within=Journal&facet-journal-id=' + str(journal_num) + '&query='
            yield scrapy.Request(
                url=next_url,
                callback=self.parseJournalLink,
                # meta={'journal_num': journal_num},
            )

        # next_url = 'https://link.springer.com/search/page/' + str(journal_page) +
        # '?search-within=Journal&facet-journal-id=' + str(journal_num) + '&query='
        # print(next_url)
        # yield scrapy.Request(
        #     url=next_url,
        #     callback=self.parseJournalLink,
        #     # meta={'journal_num': journal_num},
        # )

    def parseJournalLink(self, response):
        paper_items = response.xpath('//a[@class="title"]/@href')
        # results_num = response.xpath('//strong/text()').extract()[0].replace(',', '')
        # page_num = int(response.xpath('//span[@class="number-of-pages"]/text()').extract()[0].replace(',', ''))
        # journal_num = response.meta['journal_num']
        # journal_url = response.url
        # print(paper_items)

        for paper_item in paper_items:
            next_url = urllib.parse.urljoin("https://link.springer.com/", paper_item.extract())
            logging.info(next_url)
            yield scrapy.Request(
                url=next_url,
                callback=self.readArticle,
            )

    def parseChapter(self, response):
        chapter_page = 1
        page_num = int(response.xpath('//span[@class="number-of-pages"]/text()').extract()[0].replace(',', ''))
        chapter_num = response.meta['chapter_num']

        for chapter_page in range(1, page_num + 1):
            # logging.info("——————————————————开始从{}会议{}页爬取——————————————————".format(chapter_num, chapter_page))
            next_url = 'https://link.springer.com/search/page/' + str(chapter_page) \
                       + '?facet-content-type=Chapter&query=&facet-eisbn=' + str(chapter_num)
            yield scrapy.Request(
                url=next_url,
                callback=self.parseChapterLink,
                # meta={'chapter_num': chapter_num},
            )

    def parseChapterLink(self, response):
        paper_items = response.xpath('//a[@class="title"]/@href')
        # results_num = response.xpath('//strong/text()').extract()[0].replace(',', '')
        # page_num = int(response.xpath('//span[@class="number-of-pages"]/text()').extract()[0].replace(',', ''))
        # chapter_num = response.meta['chapter_num']
        # chapter_url = response.url

        for paper_item in paper_items:
            next_url = urllib.parse.urljoin("https://link.springer.com/", paper_item.extract())
            logging.info(next_url)
            yield scrapy.Request(
                url=next_url,
                callback=self.readChapter,
            )

    def readArticle(self, response):
        item = ReptilesItem()
        # 论文主页
        item['title'] = response.xpath('//h1[@class="c-article-title"]/text()').extract()[0]
        item['authors'] = response.xpath('//a[@data-test="author-name"]/text()').extract()
        item['abstract'] = " ".join(response.xpath('//*[@id="Abs1-content"]/p/text()').extract()).replace('\n', ' ')
        item['venue'] = response.xpath('//a[@data-test="journal-link"]/i/text()').extract()[0]
        # 论文主页
        item['url'] = response.url
        item['doi'] = response.xpath('//span[@class="c-bibliographic-information__value"]/a/text()').extract()[0]
        # 数据源
        item['source'] = 'Springer'
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
        item['year'] = ''
        item['month'] = ''
        type = response.xpath('//li[@class="c-bibliographic-information__list-item"]/p/text()').extract()
        date = response.xpath('//span[@class="c-bibliographic-information__value"]/time/text()').extract()
        for i in range(len(type)):
            if(type[i] == 'Published'):
                publishx = date[i].split(' ')
                item['year'] = publishx[2]
                item['month'] = wordtonumber[publishx[1]]
        # 论文type
        item['type'] = 'journal'
        item['video_url'] = ''
        item['video_path'] = ''
        item['thumbnail_url'] = ''
        # pdf链接
        try:
            item['pdf_url'] = response.xpath('//div[@class="c-pdf-download u-clear-both"]/a/@href')[0].extract()
            item['pdf_path'] = 'Springer/' + re.sub(r'[^\w\s]', '', item['title']).lower().replace(' ', '_') + '.pdf'
        except Exception as e:
            item['pdf_url'] = ''
            item['pdf_path'] = ''
        # 该论文被引用的数量：无
        # item['inCitations'] = [response.xpath('//span[@class="citation"]/span/text()')[0].extract()]
        item['inCitations'] = 0
        try:
            out = response.xpath('//span[@class="c-article-references__counter"]/text()')[-1].extract()
            item['outCitations'] = re.findall('\\d+', out)[-1]
        except Exception as e:
            item['outCitations'] = 0
        # print(item)
        yield item

    def readChapter(self, response):
        item = ReptilesItem()
        # 论文主页
        item['title'] = response.xpath('//h1[@class="ChapterTitle"]/text()').extract()[0]
        item['authors'] = response.xpath('//span[@class="authors__name"]/text()').extract()
        for i in range(len(item['authors'])):
            item['authors'][i] = item['authors'][i].replace("\xa0", " ")
        item['abstract'] = " ".join(response.xpath('//p[@class="Para"]/text()').extract()).replace('\n', ' ')
        item['venue'] = response.xpath('//span[@data-test="ConfSeriesName"]/text()').extract()[0]
        # 论文主页
        item['url'] = response.url
        item['doi'] = response.xpath('//span[@id="doi-url"]/text()').extract()[0]
        # 数据源
        item['source'] = 'Springer'
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
        item['year'] = publishx[2]
        item['month'] = wordtonumber[publishx[1]]
        # 论文type
        # item['type'] = response.xpath('//span[@class="test-render-category"]/text()').extract()
        item['type'] = 'conference'
        item['video_url'] = ''
        item['video_path'] = ''
        item['thumbnail_url'] = ''
        item['pdf_url'] = ''
        item['pdf_path'] = ''
        item['inCitations'] = 0
        # pdf链接：无
        # item['pdf_url'] = response.xpath('//*[@id="cobranding-and-download-availability-text"]/div/a/@href').extract()
        # 该论文被引用的数量：无
        # item['inCitations'] = [response.xpath('//span[@class="citation"]/span/text()')[0].extract()]
        try:
            out = response.xpath('//div[@class="CitationNumber"]/text()')[-1].extract()
            item['outCitations'] = re.findall("\\d+", out)[-1]
        except Exception as e:
            item['outCitations'] = 0
        yield item

    def update_process(self, type, page):
        process = {
            'type': type,
            'page': page
        }
        self.docs.update({'title': 'Springer'}, {'$set': process}, True)