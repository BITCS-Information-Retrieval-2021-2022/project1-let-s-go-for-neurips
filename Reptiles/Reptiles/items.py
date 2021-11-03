# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ReptilesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 论文标题
    title = scrapy.Field()
    # 论文摘要
    abstract = scrapy.Field()
    # 作者列表
    authors = scrapy.Field()
    # 论文doi
    doi = scrapy.Field()
    # 论文主页
    url = scrapy.Field()
    # 论文发表年份
    year = scrapy.Field()
    # 论文发表月份
    month = scrapy.Field()
    # 论文类型，只有2种值，"conference"或"journal"
    type = scrapy.Field()
    # 会议或期刊的名称
    venue = scrapy.Field()
    # 数据源，例如ACM，Springer
    source = scrapy.Field()
    # 视频在线播放链接
    video_url = scrapy.Field()
    # 视频下载到本地后的文件路径
    video_path = scrapy.Field()
    # 视频缩略图链接
    thumbnail_url = scrapy.Field()
    # PDF链接
    pdf_url = scrapy.Field()
    # PDF下载到本地后的文件路径
    pdf_path = scrapy.Field()
    # 该论文被引用的数量
    inCitations	= scrapy.Field()
    # 该论文所引用的论文数量
    outCitations = scrapy.Field()
