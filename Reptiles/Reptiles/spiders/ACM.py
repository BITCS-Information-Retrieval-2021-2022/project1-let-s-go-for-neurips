import scrapy
from Reptiles.items import ReptilesItem
import urllib
from scrapy.utils.project import get_project_settings
import logging
import re
import datetime
import calendar
from ..proxy import getProxy
import traceback
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


# test_url = 'https://dl.acm.org/doi/10.1109/ETFA.2019.8869074'

class AcmSpider(scrapy.Spider):
    name = 'ACM'
    allowed_domains = ['dl.acm.org']
    start_date = get_project_settings().get('ACM_START_DATE')
    start_date = datetime.datetime.now().replace(start_date[0], start_date[1], start_date[2]) - datetime.timedelta(
        days=1)
    start_urls = [get_project_settings().get('ACM_URL').format(start_date.year,
                                                               start_date.year,
                                                               start_date.month,
                                                               start_date.month,
                                                               start_date.day, start_date.day,
                                                               0, 20)]

    def __init__(self):
        super(AcmSpider, self).__init__()
        self.startPage = 0
        self.pageSize = 20
        self.startTime = get_project_settings().get('START_TIME')
        self.end_date = [1970, 1, 1]
        self.url = 'https://dl.acm.org/action/doSearch?expand=all&field1=AllField&A' \
                   'fterYear={}&BeforeYear={}&AfterMonth={}&BeforeMonth={}&AfterDay={}&BeforeDay={}&startPage={}&pageSize={}'
        self.proxyUpdateDelay = get_project_settings().get('PROXY_UPDATE_DELAY')
        self.count = 0

        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017, tz_aware=True)
        self.db = self.client.pc
        self.docs = self.db.get_collection("Process")
        self.config = self.docs.find_one({'title': 'ACM'})
        print(self.config)

    def parse(self, response):

        # yield scrapy.Request(
        #     url=test_url,
        #     callback=self.read
        # )
        # return

        year = self.config['year']
        month = self.config['month']
        day = self.config['day']
        start = max(0, self.config['startPage'] - 2)
        size = self.config['PageSize']
        self.size = size
        self.startPage = start
        next_url = self.url.format(year, year, month, month, day, day, self.startPage, self.pageSize)
        logging.info("——————————————————从{}年{}月{}日第{}页开始爬取——————————————————".format(year, month, day, start))
        yield scrapy.Request(
            url=next_url,
            callback=self.parse_all,
        )

    def parse_all(self, response):
        # logging.info(response.url)
        year, month, day = int(response.url.split('&')[-7].split('=')[1]), int(
            response.url.split('&')[-5].split('=')[1]), int(response.url.split('&')[-3].split('=')[1])
        now = datetime.datetime.now().replace(year, month, day)

        flag = True
        try:
            page = response.xpath('//span[@class="result__suffix"]/b/text()').extract()[0]
        except IndexError:
            flag = False
        try:
            if flag and 'Publication Date' in page:
                paper_items = response.xpath('//span[@class="hlFld-Title"]/a/@href')
                results_num = response.xpath('//span[@class="hitsLength"]/text()').extract()[0].replace(',', '')
                for paper_item in paper_items:
                    next_url = urllib.parse.urljoin("https://dl.acm.org/", paper_item.extract())
                    yield scrapy.Request(
                        url=next_url,
                        callback=self.read,
                    )

                if (self.startPage + 1) * self.pageSize < int(results_num) and self.startPage <= 100:
                    self.startPage += 1
                    # next_url = self.start_urls[0][:-3] + str(self.ID) + '&startPage=' + str(
                    #     self.startPage) + '&pageSize=' + str(self.pageSize)
                    next_url = self.url.format(year, year, month, month, day, day, self.startPage, self.pageSize)
                    yield scrapy.Request(
                        url=next_url,
                        callback=self.parse_all,
                    )
                    logging.info("——————————{}年{}月{}日第{}页爬取完毕————————".format(year, month, day, self.startPage - 1))
                    self.update_process(year, month, day, self.startPage)
                else:
                    self.startPage = 0
                    now = now - datetime.timedelta(days=1)
                    year = now.year
                    month = now.month
                    day = now.day
                    if not (year == self.end_date[0] and month == self.end_date[1] and day == self.end_date[2]):
                        next_url = self.url.format(year, year, month, month, day, day, self.startPage, self.pageSize)
                        yield scrapy.Request(
                            url=next_url,
                            callback=self.parse_all,
                        )
                    self.update_process(year, month, day, self.startPage)
                    logging.info("————————————{}年{}月{}日爬取完毕——————————".format(year, month, day))
            else:
                self.startPage = 0
                now = now - datetime.timedelta(days=1)
                year = now.year
                month = now.month
                day = now.day
                if not (year == self.end_date[0] and month == self.end_date[1] and day == self.end_date[2]):
                    next_url = self.url.format(year, year, month, month, day, day, self.startPage, self.pageSize)
                    yield scrapy.Request(
                        url=next_url,
                        callback=self.parse_all,
                    )
                    self.update_process(year, month, day, self.startPage)
                    logging.info("————————————{}年{}月{}日爬取完毕——————————".format(year, month, day))
        except ValueError:
            logging.info('这网站出错啦,' + response.url)
            self.startPage = 0
            now = now - datetime.timedelta(days=1)
            year = now.year
            month = now.month
            day = now.day
            if not (year == self.end_date[0] and month == self.end_date[1] and day == self.end_date[2]):
                next_url = self.url.format(year, year, month, month, day, day, self.startPage, self.pageSize)
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse_all,
                )
                self.update_process(year, month, day, self.startPage)
                logging.info("————————————{}年{}月{}日爬取完毕——————————".format(year, month, day))

    def read(self, response):
        # if self.count % self.proxyUpdateDelay == 0:
        # self.proxy.main()
        # logging.info("———————————————更换代理池———————————————")
        # self.count += 1

        item = ReptilesItem()
        try:
            full_info = response.xpath('//nav[@class="article__breadcrumbs separator"]/a/text()').extract()
            type = full_info[1].lower()
            type_2 = full_info[2].lower()
            if 'journal' not in type and 'conference' not in type and 'proceeding' not in type and 'title' not in type:
                return
            # 论文主页
            item['title'] = response.xpath('//h1[@class="citation__title"]/text()').extract()[0]
            try:
                item['abstract'] = response.xpath('//div[@class="abstractSection abstractInFull"]/p/text()').extract()[
                    0]
            except IndexError:
                item['abstract'] = ''
            item['authors'] = response.xpath('//span[@class="loa__author-name"]/span/text()').extract()
            try:
                item['doi'] = response.xpath('//span[@class="dot-separator"]/a/@href').extract()[0]
            except IndexError:
                item['doi'] = ''
            item['url'] = response.url
            # 发表年月
            publish = response.xpath('//span[@class="CitationCoverDate"]/text()').extract()
            publishx = publish[0].split(' ')
            item['year'] = [publishx[2]][0]
            item['month'] = wordtonumber[[publishx[1]][0]]
            if 'title' in type:
                item['type'] = 'journal' if 'periodicals' in type_2 or 'journal' in type_2 else 'conference'
                item['venue'] = full_info[3].split("'")[0]

            else:
                item['type'] = 'journal' if 'journal' in type else 'conference'
                item['venue'] = full_info[2].split("'")[0]

            # 数据源
            item['source'] = 'ACM'
            # 视频链接
            item['video_url'] = ''
            item['thumbnail_url'] = ''
            video_url = response.xpath('//div[@class="video__links table__cell-view"]/a/@href').extract()

            for url in video_url:
                if url == '#':
                    pass
                else:
                    url_complete = 'https://dl.acm.org' + url
                    item['video_url'] = url_complete
                    style = response.xpath('//stream[@class="cloudflare-stream-player"]/@src').extract()[0]
                    item[
                        'thumbnail_url'] = "https://videodelivery.net/" + style + '/thumbnails/thumbnail.jpg?time=10.0s'
            try:
                url = response.xpath('//li[@class="pdf-file"]/a/@href').extract()[0]
                item['pdf_url'] = 'https://dl.acm.org' + url
                item['pdf_path'] = './PDF/ACM/' + re.sub(r'[^\w\s]', '', item['title']).lower().replace(' ',
                                                                                                        '_') + '.pdf'
            except Exception:
                item['pdf_url'] = ''
                item['pdf_path'] = ''
            # pdf链接：无
            # 该论文被引用的数量
            item['inCitations'] = response.xpath('//span[@class="citation"]/span/text()')[0].extract()
            ref = response.xpath('//ol[contains(@class,"rlist references__list")]/li').extract()
            item['outCitations'] = str(len(ref))
            # print(item)
            yield item
        except Exception:
            # print(traceback.print_exc())
            logging.info('解析网站内容出错啦,' + response.url)

    def update_process(self, year, month, day, page):
        process = {
            'year': year,
            'month': month,
            'day': day,
            'startPage': page
        }
        self.docs.update({'title': 'ACM'}, {'$set': process}, True)
