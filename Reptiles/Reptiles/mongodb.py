import pymongo
import re

mongo = pymongo.MongoClient(host='127.0.0.1', port=27017, tz_aware=True)


def mongodb_insert(info):
    """插入及更新数据"""
    docs = mongo.pc.docs

    # docs.insert(info)

    # checksum取title中所有字母的小写
    checksum = re.sub(r'[\W\d\_]', "", info['title']).lower()
    info['checksum'] = checksum

    # 如果checksum已存在则对已有数据进行更新，否则插入
    docs.update({'checksum': info['checksum']}, {'$set': info}, True)


def mongodb_delete(field, value):
    """删除数据"""
    docs = mongo.pc.docs

    docs.delete_one({field: value})


def mongodb_find(field, value):
    """查询数据"""
    db = mongo.get_database("pc")
    docs = db.get_collection("docs")

    document = docs.find({field: value})

    return document
