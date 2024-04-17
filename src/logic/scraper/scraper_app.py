import time, re, os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from logic.scraper.parse_skidka import run_spider


def operate_image(video_locator: bool):
    picture_list = []
    pic_count = len(
        driver.find_elements(
            By.XPATH,
            '//div[@class="sw-slider-kt-mix__wrap"]//ul[@class="swiper-wrapper"]/li',
        )
    )
    try:
        base_pic_url_element = driver.find_element(
            By.XPATH, '//img[@class="photo-zoom__preview j-zoom-image hide"]'
        )
        base_pic_url = base_pic_url_element.get_attribute("src")
    except:
        time.sleep(3)
        base_pic_url_element = driver.find_element(
            By.XPATH, '//img[@class="photo-zoom__preview j-zoom-image hide"]'
        )
        base_pic_url = base_pic_url_element.get_attribute("src")

    if video_locator == False:
        pic_count += 1
    if pic_count == 1:
        picture_list.append(base_pic_url)
    else:
        for num in range(1, pic_count):
            new_pic_url = base_pic_url.replace("1.webp", str(num)) + ".webp"
            picture_list.append(new_pic_url)
    return picture_list[:5]


# https://www.wildberries.ru/catalog/193600316/detail.aspx norm
# https://www.wildberries.ru/catalog/148176220/detail.aspx sold out
def parse_wildberries(
    link: str = "https://www.wildberries.ru/catalog/193600316/detail.aspx",
):
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

    Wait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, '//ins[@class="price-block__final-price wallet"]')
        )
    )

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
    except NoSuchElementException:
        star_rating = False

    try:
        color = driver.find_element(By.XPATH, '//span[@class="color"]').get_attribute(
            "textContent"
        )
    except NoSuchElementException:
        color = False

    try:
        composition_text = driver.find_element(
            By.XPATH, '//p[@class="collapsable__content j-consist-popup"]'
        ).get_attribute("textContent")
        composition = composition_text.replace("Состав:", "").strip()
    except NoSuchElementException:
        composition = False

    try:
        size = ...
    except AttributeError:
        size = False
    try:
        video_element = driver.find_element(
            By.XPATH, '//video[@class="wb-player__video j-wb-video-player"]'
        )
        is_exist_video = not (video_element and video_element.is_displayed())
    except NoSuchElementException as e:
        is_exist_video = False

    list_of_pictures = operate_image(driver, is_exist_video)
    list_to_return.append(name)
    data = {
        "wb_id": wb_id[0],
        "name": name,
        "price": price,
        "discount_price": discount_price,
        "star_rating": star_rating,
        "url": link,
        "pic_url": str(list_of_pictures),
        "composition": composition,
        "size": "",
        "color": color,
    }
    # products_sql.insert_product(data, table_name=table_name)
    posts_count += 1
    print(data)


def start_scraper(skidka_link: str):
    global driver
    links = run_spider()
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--log-level=3")
        driver = webdriver.Firefox(options=options)
        for link in links:
            parse_wildberries(link)
    except Exception as e:
        print(e)
    finally:
        driver.close()
        driver.quit()


if __name__ == "__main__":
    start_scraper()
