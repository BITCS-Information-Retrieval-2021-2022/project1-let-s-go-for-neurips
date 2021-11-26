# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
import pymongo
import scrapy
import re
from urllib.parse import urlparse
from os.path import basename,dirname,join


class ReptilesPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient(host='10.1.114.77', port=27017, tz_aware=True)

    def process_item(self, item, spider):
        db = self.client.pc
        site = item['source']
        docs = db.get_collection(site)
        info = dict(item)
        checksum = re.sub(r'[\W\d\_]', "", info['title']).lower()
        info['checksum'] = checksum

        # 如果checksum已存在则对已有数据进行更新，否则插入
        docs.update({'checksum': info['checksum']}, {'$set': info}, True)
        return item


class PDFPipeline(FilesPipeline):
    def  get_media_requests(self, item, info):
        yield scrapy.Request(item["pdf_url"], meta={"title": item["title"]})
    
    def file_path(self, request, response=None, info=None,  item=None):
        pdf_url = urlparse(request.url).path
        pdf_name = request.meta.get("title")+'.pdf'
        return join(basename(dirname(pdf_url),basename(pdf_name)))