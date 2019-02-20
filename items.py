# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GethouseSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()          # 项目名称
    phone = scrapy.Field()          # 联系方式
    time_to_market = scrapy.Field() # 公告发出时间
    pdf_link = scrapy.Field()       # 房源详细信息pdf链接
    down_price = scrapy.Field()     # 最低价
    houses = scrapy.Field()         # 项目全部房源
    register_time = scrapy.Field()  # 登记时间
    address = scrapy.Field()        # 项目地址
