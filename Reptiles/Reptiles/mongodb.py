import pymongo
import re


class MongoManager:
    def __init__(self):
        self.myclient = pymongo.MongoClient(host='10.1.114.77', port=27017, tz_aware=True)
        self.dblist = self.myclient.list_database_names()
        self.mydb = None
        self.collist = None
        self.mycol = None


class MongoManager:
    def __init__(self):
        self.myclient = pymongo.MongoClient(host='10.1.114.77', port=27017, tz_aware=True)
        self.dblist = self.myclient.list_database_names()
        self.mydb = None
        self.collist = None
        self.mycol = None

    def mongodb_insert(self, site, info):
        """插入及更新数据"""
        db = self.myclient.pc
        docs = db.get_collection(site)

        # docs.insert(info)

        # checksum取title中所有字母的小写
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
    db = MongoManager()
    db.mongodb_insert("Process", {
        'title':'ACM',
        'year': 2021,
        'month': 11,
        'day': 23,
        'startPage': 0,
        'PageSize': 20
    })
