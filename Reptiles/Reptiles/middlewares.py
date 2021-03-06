# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.http import HtmlResponse
from twisted.internet import task
from fake_useragent import UserAgent
import logging
from selenium import webdriver
import time
import random
import requests


class ReptilesSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ReptilesDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware(object):
    '''
    随机更换user-agent
    模仿并替换site-package/scrapy/downloadermiddlewares源代码中的
    useragent.py中的UserAgentMiddleware类
    '''

    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent(verify_ssl=False)
        # 可读取在settings文件中的配置，来决定开源库ua执行的方法，默认是random，也可是ie、Firefox等等
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    # 更换用户代理逻辑在此方法中
    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        # logging.info('$-Message From Random UserAgent Middleware: ' + get_ua())
        request.headers.setdefault('User-Agent', get_ua())


class JSMiddleware(object):
    def process_request(self, request, spider):
        driver = webdriver.PhantomJS("/Users/reacubeth/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs")  # 指定使用的浏览器
        driver.get(request.url)
        time.sleep(1)
        # js = "var q=document.documentElement.scrollTop=10000"
        js = "window.scrollTo(0,document.body.scrollHeight)"

        driver.execute_script(js)
        time.sleep(random.randint(1, 2))

        body = driver.page_source
        print("访问" + request.url)
        return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)


class StatisticsMiddleware(object):
    def __init__(self, stats):
        self.stats = stats
        # 每隔多少秒监控一次已抓取数量
        self.time = 10.0

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        instance = cls(crawler.stats)
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        return instance

    def spider_opened(self):
        self.tsk = task.LoopingCall(self.collect)
        self.tsk.start(self.time, now=True)

    def spider_closed(self):
        scrapy_count = self.stats.get_value('item_scraped_count')
        print(scrapy_count)
        if self.tsk.running:
            self.tsk.stop()

    def collect(self):
        # 这里收集stats并写入相关的储存。
        # 目前展示是输出到终端
        scrapy_count = self.stats.get_value('item_scraped_count')
        if scrapy_count:
            print(scrapy_count)


class ProxiesMiddleware(object):
    def __init__(self, settings):
        super(ProxiesMiddleware, self).__init__()
        self.step = 0
        self.proxypool_url = 'http://127.0.0.1:5555/random'
        self.proxy = self.get_random_proxy()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def get_random_proxy(self):
        proxy = requests.get(self.proxypool_url).text.strip()
        logging.info('---get_random_proxy--- ' + str(proxy))
        return proxy

    def process_request(self, request, spider):
        self.step += 1
        if self.step % 1000 == 0:
            self.proxy = self.get_random_proxy()
        request.meta['proxy'] = 'http://' + self.proxy
        request.headers["Connection"] = "close"
