import os
from Reptiles.Reptiles.data_manager import MongoManager


def prepare_folder():
    folder_list = ['./Reptiles/PDF', './Reptiles/PDF/ACM', './Reptiles/PDF/ScienceDirect', './Reptiles/PDF/Springer']
    for folder in folder_list:
        if not os.path.exists(folder):
            os.makedirs(folder)


def prepare_mongodb():
    db = MongoManager()
    db.mongodb_insert("Process", {
        'title': 'ACM',
        'year': 2000,
        'month': 1,
        'day': 1,
        'startPage': 0,
        'PageSize': 20
    })

    db.mongodb_insert("Process", {
        'title': 'Springer',
        'type': 'Journal',
        'page': 1
    })

    db.mongodb_insert("Process", {
        'title': 'ScienceDirect',
        'year': '2021',
        'venue_id': 0
    })


if __name__ == '__main__':
    prepare_mongodb()
    prepare_folder()
    print('爬虫准备完毕！')
