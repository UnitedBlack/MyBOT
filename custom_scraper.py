from playwright.async_api import async_playwright
from playwright._impl._api_types import TimeoutError as TimeoutPlaywright
import time
import logging
import colorlog
import re
import asyncio
from pprint import pprint


async def operate_image(video):
    picture_list = []
    pic_count = await page.locator(
        '//div[@class="sw-slider-kt-mix__wrap"]//ul[@class="swiper-wrapper"]/li'
    ).count()
    base_pic_url_element = await page.query_selector(
        '//img[@class="photo-zoom__preview j-zoom-image hide"]'
    )
    try:
        base_pic_url = await base_pic_url_element.get_attribute("src")
    except:
        await asyncio.sleep(1)
        base_pic_url_element = await page.query_selector(
            '//img[@class="photo-zoom__preview j-zoom-image hide"]'
        )
        base_pic_url = await base_pic_url_element.get_attribute("src")
    if video == False:
        pic_count += 1
    if pic_count == 1:
        picture_list.append(base_pic_url)
    else:
        for num in range(1, pic_count):
            new_pic_url = base_pic_url.replace("1.webp", str(num)) + ".webp"
            picture_list.append(new_pic_url)
    return picture_list[:5]


async def parse_wildberries(url):
    try:
        await page.goto(url)
    except TimeoutPlaywright:
        time.sleep(3)
        await page.goto(url)
    time.sleep(2)
    await page.wait_for_selector("h1")
    await page.wait_for_selector('//div[@class="details__header-wrap hide-mobile"]')
    wb_id = re.findall(r"\d+", url)
    try:
        sold_out_element = await page.query_selector(
            '//span[@class="sold-out-product__text"]'
        )
        sold_out = await sold_out_element.is_visible()
    except AttributeError:
        sold_out = False
    if sold_out:
        return "Product is sold out"

    name_element = await page.query_selector("h1")
    name = await name_element.text_content()
    price_text_element = await page.query_selector(
        '//ins[@class="price-block__final-price"]'
    )
    price_text = await price_text_element.text_content()
    price = price_text.replace("₽", "").replace(" ", "").replace("\xa0", "")
    discount_price_text_element = await page.query_selector(
        '//del[@class="price-block__old-price j-wba-card-item-show"]'
    )
    discount_price_text = await discount_price_text_element.text_content()
    discount_price = (
        discount_price_text.replace("₽", "").replace(" ", "").replace("\xa0", "")
    )
    try:
        description_element = await page.query_selector(
            '//p[@class="collapsable__text"]'
        )
        description_text = await description_element.text_content()
        description = description_text.split(".")[1:3]
    except:
        description = False
    try:
        star_rating_element = await page.query_selector(
            '//span[@class="product-review__rating address-rate-mini address-rate-mini--sm"]'
        )
        star_rating = await star_rating_element.text_content()
    except AttributeError:
        star_rating = False
    try:
        color_element = await page.query_selector('//span[@class="color"]')
        color = await color_element.text_content()
    except AttributeError:
        color = False
    try:
        composition_text_element = await page.query_selector(
            '//p[@class="collapsable__content j-consist-popup"]'
        )
        composition_text = await composition_text_element.text_content()
        composition = composition_text.replace("Состав:", "").strip()
    except AttributeError:
        composition = False
    try:
        size = ...
    except AttributeError:
        size = False

    video_element = await page.query_selector(
        '//video[@class="wb-player__video j-wb-video-player"]'
    )
    is_exist_video = not (video_element and not await video_element.is_hidden())

    list_of_pictures = await operate_image(is_exist_video)
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
    return data


async def main(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        global page
        page = await context.new_page()
        data = await parse_wildberries(url)
    print("Done")
    return data


if __name__ == "__main__":
    asyncio.run(main(url="https://www.wildberries.ru/catalog/148176220/detail.aspx"))