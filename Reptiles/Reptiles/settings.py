# Scrapy settings for Reptiles project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import datetime

BOT_NAME = 'Reptiles'

SPIDER_MODULES = ['Reptiles.spiders']
NEWSPIDER_MODULE = 'Reptiles.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Reptiles (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Time
START_TIME = datetime.datetime.now()
PROXY_UPDATE_DELAY = 150
# URL
ACM_URL = 'https://dl.acm.org/action/doSearch?expand=all&field1=AllField&AfterYear={' \
          '}&BeforeYear={}&AfterMonth={}&BeforeMonth={}&AfterDay={}&BeforeDay={}&startPage={}&pageSize={}'
ACM_START_DATE = [2020, 10, 30]
# Retry Setting
# Retry many times since proxies often fail
RETRY_TIMES = 10
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]

# Proxy Setting
# RANDOM_UA_TYPE = 'random'  # 或者指定浏览器 firefox、chrome...
PROXY_LIST = './Reptiles/configs/proxylist_big.txt'
# 代理模式
# 0 = Every requests have different proxy
# 1 = Take only one proxy from the list and assign it to every requests
# 2 = Put a custom proxy to use in the settings
PROXY_MODE = 0
# 如果使用模式2，将下面解除注释：
# CUSTOM_PROXY = "http://host1:port"
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'acaSpider (+http://www.yourdomain.com)'

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'acaSpider.middlewares.AcaspiderSpiderMiddleware': 543,
# }
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy_proxies.RandomProxy': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'Reptiles.middlewares.RandomUserAgentMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # 'Reptiles.middlewares.ProxiesMiddleware': 700,
}
DOWNLOAD_TIMEOUT = 100
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# SCHEDULER_PERSIST = True
# REDIS_URL = "redis://127.0.0.1:6379"
# REDIS_HOST = "127.0.0.1"
# REDIS_PORT = 6379
# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'Reptiles.pipelines.ReptilesPipeline': 100,
    'Reptiles.pipelines.PDFPipeline': 200,
}
FILES_STORE = './'
LOG_FILE_PATH = './Logs/{}_Scrapy_{}_{}_{}.log'.format(BOT_NAME, START_TIME.year, START_TIME.month, START_TIME.day)
LOG_LEVEL = 'INFO'
LOG_FILE = LOG_FILE_PATH
