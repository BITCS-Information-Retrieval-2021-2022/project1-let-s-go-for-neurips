# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
import pymongo
import scrapy
import re
from urllib.parse import urlparse
from os.path import basename, dirname, join

from .data_manager import ElasticsearchManager


class ReptilesPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient(host='10.1.114.77', port=27017, tz_aware=True)
        self.ela_client = ElasticsearchManager()

    def process_item(self, item, spider):
        db = self.client.pc
        # site = item['source']
        docs = db.get_collection("Paper")
        info = dict(item)
        checksum = re.sub(r'[\W\d\_]', "", info['title']).lower()
        info['checksum'] = checksum

        # 如果checksum已存在则对已有数据进行更新，否则插入
        docs.update({'checksum': info['checksum']}, {'$set': info}, True)

        count = docs.find({'checksum': info['checksum']}).count()
        if count > 0:
            info['year'] = int(info['year'])
            info['month'] = int(info['month'])
            info['inCitations'] = int(info['inCitations'])
            info['outCitations'] = int(info['outCitations'])
            self.ela_client.elas_insert('paper', info)
        return item


class PDFPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        if item['pdf_url'] != "" and item['pdf_path'] != "":
            yield scrapy.Request(item["pdf_url"], meta={"path": item["pdf_path"]})

    def file_path(self, request, response=None, info=None):
        return request.meta.get("path")


class VideoPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(item["video_url"], meta={"path": item["video_path"]})

    def file_path(self, request, response=None, info=None):
        return request.meta.get("path")


class VideoPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(item["video_url"], meta={"path": item["video_path"]})

    def file_path(self, request, response=None, info=None):
        return request.meta.get("path")
