from playwright.sync_api import sync_playwright
import time


def operate_image(video):
    picture_list = []
    pic_count = page.locator('//div[@class="sw-slider-kt-mix__wrap"]//ul[@class="swiper-wrapper"]/li').count()
    base_pic_url = page.query_selector('//img[@class="photo-zoom__preview j-zoom-image hide"]').get_attribute("src")
    if video == False: pic_count += 1
    for num in range(1, pic_count):
        new_pic_url = base_pic_url.replace("1.webp", str(num)) + ".webp"
        picture_list.append(new_pic_url)
    return picture_list


def parse_main_page():
    page.goto("https://www.wildberries.ru/catalog/148238798/detail.aspx?targetUrl=SG")
    page.wait_for_selector('h1')
    # проверку на то что "товар закончился"
    # Обязательные данные
    name = page.query_selector("h1").text_content()
    price = page.query_selector('//ins[@class="price-block__final-price"]').text_content().replace(' ', '').replace('₽', '')
    discount_price = page.query_selector('//del[@class="price-block__old-price j-wba-card-item-show"]').text_content().replace(' ', '').replace('₽', '')
    star_rating = page.query_selector('//span[@class="product-review__rating address-rate-mini address-rate-mini--sm"]').text_content()
    # дополнительные данные
    try:
        color = page.query_selector('//span[@class="color"]').text_content()
    except(AttributeError):
        color = False
    try:
        composition = page.query_selector('//p[@class="collapsable__content j-consist-popup"]').text_content().replace('Состав:', '')[41:]
    except(AttributeError):
        composition = False
    try:
        is_exist_video = page.query_selector('//video[@class="wb-player__video j-wb-video-player"]').is_hidden()
    except(AttributeError):
        is_exist_video = False
    list_of_pictures = operate_image(is_exist_video)
    print(list_of_pictures)
    


# def init():
with sync_playwright() as p:
    browser = p.firefox.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    # page.goto("https://skidka7.com/")
    parse_main_page()
        
        
        
# id name discount_price price star_rating url pic_url composition size color
# https://skidka7.com/discount/beauty/all
# https://skidka7.com/discount/cwomen/all
# url = //div[@class="panel panel-flat padding9"]/a[1]  
# wildbebra
