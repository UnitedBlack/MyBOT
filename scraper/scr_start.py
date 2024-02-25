from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sp_test import SkidkaSpider


def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl(SkidkaSpider)
    process.start()
    print(SkidkaSpider.links)


print(run_spider())
