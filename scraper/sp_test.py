import scrapy
from scrapy import signals
from scrapy.exceptions import DontCloseSpider

links = []


class SkidkaSpider(scrapy.Spider):
    name = "Skidka"
    start_urls = ["https://skidka7.com/discount/cwomen/all"]

    def parse(self, response):
        self.data = []
        cards = response.xpath(
            '//div[@class="col-xl-2 col-lg-2 col-md-3 col-sm-3 col-xs-6"]'
        )
        for card in cards:
            sold_out_elem = card.xpath('.//p[@style="color: red"]/text()').get()
            if sold_out_elem == "\nЗакончился\n":  # почему-то получает \n
                continue
            url_element = card.xpath('.//div[@class="panel panel-flat padding9"]/a[1]')
            url = url_element.xpath("@href").get()
            self.data.append(url)

    def close(self, reason):
        global links
        links = self.data