# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import GethouseSpiderItem
from urllib.request import urlopen
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO


class GetHouseSpider(scrapy.Spider):
    name = 'getHouse'
    allowed_domains = ['182.136.72.132:443', '182.140.147.106:443', 'cdfangxie.com']
    start_urls = ['https://www.cdfangxie.com/Infor/type/typeid/36.html']

    def parse(self, response):
        item_link = response.xpath("//ul[@class='ul_list']/li/span[1]/a/@href").extract()
        # 循环访问每一个楼盘详情页
        for i in item_link:
            yield scrapy.Request('https://www.cdfangxie.com' + i, callback=self.parse_detail,
                                 dont_filter=False)
        # yield scrapy.Request('https://www.cdfangxie.com/Infor/index/id/5465.html', callback=self.parse_detail,
        #                      dont_filter=False)
        # 循环下一页
        # for j in range(2, 57):
        #     next_page = 'https://www.cdfangxie.com/Infor/type/typeid/36.html?&p='+str(j)
        #     yield scrapy.Request(next_page, callback=self.parse, dont_filter=False)

    # 获取楼盘详情页中的部分数据
    def parse_detail(self, response):
        item = GethouseSpiderItem()
        item['title'] = response.xpath("//div[@class='infor']/p[1]/b/span/span/text()").extract_first()
        item['phone'] = response.xpath("//div[@class='infor']/p[4]/span/span[2]/text()").extract_first()[1:]
        item['pdf_link'] = response.xpath("//div[@class='infor']/p/span/span/a/@href").extract_first()
        info = response.xpath("//div[@class='infor']").extract_first()
        index_time = info.find("上市时间") + len("上市时间")
        detail_time = info[index_time:index_time + 20]
        item['time_to_market'] = ''.join(re.findall('\d+[\\.*]?\\d*', detail_time))
        # 获取pdf文档中详细信息
        if item['pdf_link'].endswith('.pdf'):
            print("是pdf文档")
            pdf_content = self.parse_online_pdf(item['pdf_link'])
            # 获取最低价
            index_down_price_start = pdf_content.find("装修价款）") + len("装修价款）")
            index_down_price_end = pdf_content.find("计；")
            down_price = pdf_content[index_down_price_start: index_down_price_end]
            item['down_price'] = ''.join(re.findall('[\u4e00-\u9fa5_0-9\.]*', down_price))
            # 获取全部房源
            index_houses_start = pdf_content.find("全部准售房源") + len("全部准售房源")
            index_houses_end = pdf_content.find("上述房源")
            houses = pdf_content[index_houses_start: index_houses_end]
            item['houses'] = ''.join(re.findall('[\u4e00-\u9fa5_a-zA-Z0-9\.,㎡]*', houses))
            # 获取登记时间
            index_register_time_start = pdf_content.find("（一）登记时间：") + len("（一）登记时间：")
            index_register_time_end = pdf_content.find("购房登记时，登记购房人应")
            register_time = pdf_content[index_register_time_start: index_register_time_end]
            item['register_time'] = ''.join(re.findall('[\u4e00-\u9fa5_0-9\,:-]*', register_time))
            # 获取地址
            index_Information_publicity = pdf_content.find("四、信息公示") + len("四、信息公示")
            Information_publicity = pdf_content[index_Information_publicity: index_Information_publicity+200]
            index_address_start = Information_publicity.find("（二）公示地点：") + len("（二）公示地点：")
            index_address_end = Information_publicity.find("（三）公示内容：")
            address = Information_publicity[index_address_start: index_address_end]
            item['address'] = ''.join(re.findall('[\u4e00-\u9fa5_a-zA-Z0-9\,:()]*', address))
        else:
            print("不是pdf文档")
        yield item

    def parse_online_pdf(self, url):
        pdfFile = urlopen(url)
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        process_pdf(rsrcmgr, device, pdfFile)
        device.close()
        content = retstr.getvalue()
        retstr.close()
        return content
