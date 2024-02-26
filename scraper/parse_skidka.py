import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

links = []


class SkidkaSpider(scrapy.Spider):
    name = "Skidka"
    start_urls = [
        "https://skidka7.com/discount/cwomen/all?page=1",
        "https://skidka7.com/discount/cwomen/all?page=2",
        "https://skidka7.com/discount/cwomen/all?page=3",
    ]

    def parse(self, response):
        self.data = []
        cards = response.xpath(
            '//div[@class="col-xl-2 col-lg-2 col-md-3 col-sm-3 col-xs-6"]'
        )
        for i, card in enumerate(cards):
            sold_out_elem = card.xpath('.//p[@style="color: red"]/text()').get()
            if sold_out_elem == "\nЗакончился\n":  # почему-то получает \n
                continue
            url_element = card.xpath('.//div[@class="panel panel-flat padding9"]/a[1]')
            url = url_element.xpath("@href").get()
            links.append(url)


def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl(SkidkaSpider)
    process.start()
    return links
