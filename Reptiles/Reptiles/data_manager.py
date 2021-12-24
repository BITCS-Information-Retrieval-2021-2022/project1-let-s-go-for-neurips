import pymongo
import re
from elasticsearch import Elasticsearch
import datetime
import ndjson

import json


def convert_json():
    docs = []

    with open("./ACM.json", 'rb') as load_f:
        for line in load_f:
            docs.append(json.loads(line))
    for dic in docs:
        del dic['_id']

    with open("./test_out.json", "w") as dump_f:
        for dic in docs:
            json.dump(dic, dump_f)
            if dic != docs[-1]:
                dump_f.write('\n')


class ElasticsearchManager:
    def __init__(self):
        self.es = Elasticsearch("localhost:9200")

    def elas_insert(self, index, data):
        self.es.index(index=index, document=data)

    def elas_query(self):
        print(self.es.search(index="test"))

    def elas_delete(self, index):
        self.es.indices.delete(index=index, ignore=[400, 404])

    def batch_inset(self, path):
        with open(path, 'r') as load_f:
            load_dict = ndjson.load(load_f)
            print(len(load_dict))
            for index, item in enumerate(load_dict):
                if index % 10000 == 0:
                    print(index)
                video_path = ''
                if item['source'] == 'ACM' and item['video_url'] != '':
                    video_path = './VIDEO/ACM/' + re.sub(r'[^\w\s]', '', item['title']).lower().replace(' ',
                                                                                                        '_') + '.mp4'
                if item['inCitations'] == "":
                    item['inCitations'] = 0

                if item['outCitations'] == "":
                    item['outCitations'] = 0
                if item['year'] == "":
                    item['year'] = 0
                if item['month'] =="":
                    item['month'] = 0
                new_item = {
                    "title": item['title'],
                    "abstract": item['abstract'],
                    "authors": item['authors'],
                    "doi": item['doi'],
                    "url": item['url'],
                    "year": int(item['year']),
                    "month": int(item['month']),
                    "type": item['type'],
                    "venue": item['venue'],
                    "source": item['source'],
                    "video_url": item['video_url'],
                    "video_path": video_path,
                    "thumbnail_url": item['thumbnail_url'],
                    "pdf_url": item['pdf_url'],
                    "pdf_path": item['pdf_path'],
                    "inCitations": int(item['inCitations']),
                    "outCitations": int(item['outCitations']),
                }
                self.elas_insert('paper', new_item)


class MongoManager:
    def __init__(self):
        self.myclient = pymongo.MongoClient(host='127.0.0.1', port=27017, tz_aware=True)
        self.dblist = self.myclient.list_database_names()
        self.mydb = None
        self.collist = None
        self.mycol = None

    def mongodb_insert(self, site, info):
        """插入及更新数据"""
        db = self.myclient.pc
        docs = db.get_collection(site)

        # docs.insert(info)

        # checksum取tle中所有字母的小写
        checksum = re.sub(r'[\W\d\_]', "", info['title']).lower()
        info['checksum'] = checksum

        # 如果checksum已存在则对已有数据进行更新，否则插入
        docs.update({'checksum': info['checksum']}, {'$set': info}, True)

    def mongodb_delete(self, site, field, value):
        """删除数据"""
        db = self.myclient.pc
        docs = db.get_collection(site)

        docs.delete_one({field: value})

    def mongodb_find(self, site, field, value):
        """查询数据"""
        db = self.myclient.get_database("pc")
        docs = db.get_collection(site)

        document = docs.find({field: value})

        return document


if __name__ == '__main__':
    ela = ElasticsearchManager()
    ela.batch_inset('/home/liuchi/wh/bit/project1-let-s-go-for-neurips/paper_final.json')
    # ela.elas_insert({
    #     'title':'ACM',
    #     'year': 2021,
    #     'month': 11,
    #     'day': 23,
    #     'time':datetime.datetime.now()
    # })
    # ela.elas_query()
    #ela.elas_delete('paper')
    # ela.elas_delete('test')
    # db = MongoManager()
    # db.mongodb_insert("Process", {
    #     'title':'ACM',
    #     'year': 2021,
    #     'month': 11,
    #     'day': 23,
    #     'startPage': 0,
    #     'PageSize': 20
    # })
