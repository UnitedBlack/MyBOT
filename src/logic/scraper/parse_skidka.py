from typing import Any
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

links = []


class SkidkaSpider(scrapy.Spider):
    name = "Skidka"

    def __init__(self, skidka_link=None, *args, **kwargs):
        super(SkidkaSpider, self).__init__(*args, **kwargs)
        self.skidka_link = skidka_link
        self.start_urls = [
            f"{self.skidka_link}?page=1",
            f"{self.skidka_link}?page=2",
            f"{self.skidka_link}?page=3",
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
            print(i)
            links.append(url)


def run_spider(skidka_link):
    process = CrawlerProcess(get_project_settings())
    process.crawl(SkidkaSpider, skidka_link=skidka_link)
    process.start()
    return links


# def skidka_site_parser(skidka_link):
#     global driver
#     links = skidka_site_parser()
#     try:
#         options = Options()
#         options.add_argument("--headless")
#         options.add_argument("--log-level=3")
#         driver = webdriver.Firefox(options=options)
#         for link in links:
#             parse_wildberries(link)
#     except Exception as e:
#         print(e)
#     finally:
#         driver.close()
#         driver.quit()
