# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter

import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log


class GethouseSpiderPipeline(object):
    def process_item(self, item, spider):
        return item

# 调用scrapy提供的json export导出json文件


class JsonExporterPipleline(object):
    def __init__(self):
        self.file = open('House.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

# 导出到mongoDB中
class MongoDBPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(settings.get('MONGODB_SERVER'), settings.get('MONGODB_PORT'))
        db = connection[settings.get('MONGODB_DB')]
        self.collection = db[settings.get('MONGODB_COLLECTION')]

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
            if valid:
                self.collection.insert(dict(item))
                log.msg("Houses Add To MongoDB Successfully!", level=log.DEBUG, spider=spider)
                return item

