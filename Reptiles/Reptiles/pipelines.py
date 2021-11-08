# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import re

class ReptilesPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017, tz_aware=True)
    def process_item(self, item, spider):
        docs = self.client.pc.docs
        info = dict(item)
        checksum = re.sub(r'[\W\d\_]', "", info['title']).lower()
        info['checksum'] = checksum

        # 如果checksum已存在则对已有数据进行更新，否则插入
        docs.update({'checksum': info['checksum']}, {'$set': info}, True)
        return item
