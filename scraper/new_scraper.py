import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

driver = webdriver.Firefox()


class WebDriverContext:
    def __init__(self, driver: webdriver) -> None:
        self.driver = driver

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
        self.driver.quit()


def parse_main_page(link):
    driver.get(link)
    urls_list = []
    for page in range(1):
        driver.get(f"{link}?page={page}")
        card_elements = driver.find_elements(
            By.XPATH, '//div[@class="col-xl-2 col-lg-2 col-md-3 col-sm-3 col-xs-6"]'
        )
        time.sleep(1)
        for card in card_elements:
            url_element = card.find_element(
                By.XPATH, '//div[@class="panel panel-flat padding9"]/a[1]'
            )
            try:
                url = url_element.get_attribute("href")
            except:
                print("Не могу получить ссылку")
                url = url_element.get_attribute("href")
            urls_list.append(url)
    # print(urls_list)


def start():
    with WebDriverContext(driver):
        parse_main_page("https://skidka7.com/discount/cwomen/all")


if __name__ == "__main__":
    start()
