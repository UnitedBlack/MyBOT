from playwright.async_api import async_playwright
from playwright._impl._api_types import TimeoutError as TimeoutPlaywright
import sql
import time
import logging
import colorlog
import re
import asyncio
from pprint import pprint

super_list = []
index = 0


async def operate_image(video):
    picture_list = []
    pic_count = await page.locator(
        '//div[@class="sw-slider-kt-mix__wrap"]//ul[@class="swiper-wrapper"]/li'
    ).count()
    base_pic_url_element = await page.query_selector(
        '//img[@class="photo-zoom__preview j-zoom-image hide"]'
    )
    base_pic_url = await base_pic_url_element.get_attribute("src")
    if video == False:
        pic_count += 1
    for num in range(1, pic_count):
        new_pic_url = base_pic_url.replace("1.webp", str(num)) + ".webp"
        picture_list.append(new_pic_url)
    return picture_list[:5]


async def parse_wildberries(urls, connection, custom=False):
    global posts_count
    posts_count = 0
    list_to_return = []
    logger.debug("Parsing wildberries cards")
    logger.debug(f"Число вб страниц: {len(urls)}")
    for url in urls:
        try:
            in_database = sql.is_product_in_database(url, connection)
            if in_database:
                product_in_db = True
                logger.warning(f"{url} Product in DB")
                continue
            logger.info(f"{url} not in DB")
            try:
                await page.goto(url)
            except TimeoutPlaywright:
                logger.warning("Couldn't load page, trying again...")
                await page.goto(url)

            await page.wait_for_selector("h1")
            await page.wait_for_selector(
                '//div[@class="details__header-wrap hide-mobile"]'
            )
            wb_id = re.findall(r"\d+", url)
            try:
                sold_out_element = await page.query_selector(
                    '//span[@class="sold-out-product__text"]'
                )
                sold_out = await sold_out_element.is_visible()
            except AttributeError:
                sold_out = False

            if sold_out:
                continue
            pic_count = await page.locator(
                '//div[@class="sw-slider-kt-mix__wrap"]//ul[@class="swiper-wrapper"]/li'
            ).count()
            if pic_count == 1: continue
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
                discount_price_text.replace("₽", "")
                .replace(" ", "")
                .replace("\xa0", "")
            )

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
            list_to_return.append(name)
            # global data
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
            sql.insert_product(data, connection)
            posts_count += 1
        except AttributeError as e:
            logger.critical(f"Error {e} in url \n{url}")
            continue
        if custom:
            return data


async def parse_main_page(skidka_link, connection):
    logger.debug("Parsing main page...")

    list_of_urls = []

    for current_page in range(1, 2):
        logger.info(f"Current page: {current_page}")
        await page.goto(f"{skidka_link}?page={current_page}")
        cards = await page.query_selector_all(
            '//div[@class="col-xl-2 col-lg-2 col-md-3 col-sm-3 col-xs-6"]'
        )
        for card in cards:
            sold_out_element = await card.query_selector('//p[@style="color: red"]')
            sold_out = sold_out_element and await sold_out_element.is_visible()
            if sold_out:
                continue
            url_element = await card.query_selector(
                '//div[@class="panel panel-flat padding9"]/a[1]'
            )
            url = await url_element.get_attribute("href")
            list_of_urls.append(url)
    await parse_wildberries(list_of_urls, connection)


async def main(link, connection, custom=False):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        global page
        page = await context.new_page()
        if custom:
            data = await parse_wildberries(link, connection, custom=True)
            return data
        else:
            await parse_main_page(link, connection)
    print("Done")
    return posts_count


logger = logging.getLogger("WB")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        "DEBUG": "green",
        "INFO": "purple",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
    },
    secondary_log_colors={},
    style="%",
)
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == "__main__":
    # asyncio.run(initialize())
    asyncio.run(main(link="https://skidka7.com/discount/cwomen/all"))
    # asyncio.run(parse_main_page())
    logger.debug("Done")
# else:
#     asyncio.run(main())
