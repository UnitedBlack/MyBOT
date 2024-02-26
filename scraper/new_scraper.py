import time, re, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from parse_skidka import run_spider

driver = webdriver.Firefox()


class WebDriverContext:
    def __init__(self, driver: webdriver) -> None:
        self.driver = driver

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
        self.driver.quit()


# https://www.wildberries.ru/catalog/193600316/detail.aspx norm
# https://www.wildberries.ru/catalog/148176220/detail.aspx sold out
def parse_wildberries(link="https://www.wildberries.ru/catalog/193600316/detail.aspx"):
    posts_count = 0
    list_to_return = []
    wb_id = re.findall(r"\d+", link)

    try:
        driver.get(link)
    except Exception as e:
        print(e)
        exit()
    try:
        Wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//h1")))
        print("Presented")
    except Exception as e:
        print(e)

    try:
        sold_out_element = driver.find_element(
            By.XPATH, '//span[@class="sold-out-product__text"]'
        )
        sold_out = sold_out_element.is_displayed()
    except NoSuchElementException:
        sold_out = False
    if sold_out:
        print("sold out")
        return
    pic_count = len(
        driver.find_elements(
            By.XPATH,
            '//div[@class="sw-slider-kt-mix__wrap"]//ul[@class="swiper-wrapper"]/li',
        )
    )
    if pic_count == 1:
        print("Кринж")
        return
    name = driver.find_element(By.XPATH, "//h1").get_attribute("textContent")

    driver.wait_for_selector('//ins[@class="price-block__final-price wallet"]')

    price_text = driver.find_element(
        By.XPATH, '//ins[@class="price-block__final-price wallet"]'
    ).get_attribute("textContent")
    price = price_text.replace("₽", "").replace(" ", "").replace("\xa0", "")

    discount_price_text = driver.find_element(
        By.XPATH, '//del[@class="price-block__old-price"]'
    ).get_attribute("textContent")

    discount_price = (
        discount_price_text.replace("₽", "").replace(" ", "").replace("\xa0", "")
    )

    try:
        description_text = driver.find_element(
            By.XPATH, '//p[@class="collapsable__text"]'
        ).get_attribute("textContent")
        description = description_text.split(".")[1:3]
    except:
        description = False

    try:
        star_rating = driver.find_element(
            By.XPATH,
            '//span[@class="product-review__rating address-rate-mini address-rate-mini--sm"]',
        ).get_attribute("textContent")
    except AttributeError:
        star_rating = False

    try:
        color = driver.find_element(By.XPATH, '//span[@class="color"]').get_attribute(
            "textContent"
        )
    except AttributeError:
        color = False

    try:
        composition_text = driver.find_element(
            By.XPATH, '//p[@class="collapsable__content j-consist-popup"]'
        ).get_attribute("textContent")
        composition = composition_text.replace("Состав:", "").strip()
    except AttributeError:
        composition = False

    try:
        size = ...
    except AttributeError:
        size = False

    video_element = driver.find_element(
        By.XPATH, '//video[@class="wb-player__video j-wb-video-player"]'
    )
    is_exist_video = not (video_element and video_element.is_displayed())

    list_of_pictures = operate_image(is_exist_video)
    list_to_return.append(name)
    data = {
        "wb_id": wb_id[0],
        "name": name,
        "price": price,
        "discount_price": discount_price,
        "star_rating": star_rating,
        "url": url,
        "pic_url": str(list_of_pictures),
        "composition": composition,
        "size": "",
        "color": color,
    }
    # products_sql.insert_product(data, table_name=table_name)
    posts_count += 1
    # try:
    #     ...
    # except Exception as e:
    #     print(e)

    # urls_list = []
    # for driver in range(1):
    #     driver.get(f"{link}?driver={driver}")
    #     card_elements = driver.find_elements(
    #         By.XPATH, '//div[@class="col-xl-2 col-lg-2 col-md-3 col-sm-3 col-xs-6"]'
    #     )
    #     time.sleep(1)
    #     for card in card_elements:
    #         url_element = card.find_element(
    #             By.XPATH, '//div[@class="panel panel-flat padding9"]/a[1]'
    #         )
    #         try:
    #             url = url_element.get_attribute("href")
    #         except:
    #             print("Не могу получить ссылку")
    #             url = url_element.get_attribute("href")
    #         urls_list.append(url)
    # print(urls_list)


def start():
    # links = run_spider()
    # print(links)
    with WebDriverContext(driver):
        parse_wildberries()
        # for link in links:


if __name__ == "__main__":
    start()
