from playwright.sync_api import sync_playwright
import sql
import time
import logging
import colorlog

super_list = []
index = 0



def operate_image(video):
    picture_list = []
    pic_count = page.locator('//div[@class="sw-slider-kt-mix__wrap"]//ul[@class="swiper-wrapper"]/li').count()
    base_pic_url = page.query_selector('//img[@class="photo-zoom__preview j-zoom-image hide"]').get_attribute("src")
    if video == False: pic_count += 1
    for num in range(1, pic_count):
        new_pic_url = base_pic_url.replace("1.webp", str(num)) + ".webp"
        picture_list.append(new_pic_url)
    return picture_list


def parse_wildberries(list_to_return = []):
    logger.debug("Parsing wildberries cards")
    with open("url_list.txt", "r") as file:
        urls = file.read().splitlines()
    logger.debug(f"Число вб страниц: {len(urls)}")
    for url in urls:
        try:
            page.goto(url, wait_until='domcontentloaded')
            page.wait_for_selector('h1')
            time.sleep(1)
            
            try: 
                sold_out = page.query_selector('//span[@class="sold-out-product__text"]').is_visible()
            except(AttributeError):
                sold_out = False
                
            if sold_out: continue
            
            name = page.query_selector("h1").text_content()
            price = page.query_selector('//ins[@class="price-block__final-price"]').text_content().replace(' ', '').replace('₽', '')
            discount_price = page.query_selector('//del[@class="price-block__old-price j-wba-card-item-show"]').text_content().replace(' ', '').replace('₽', '')
            try:
                star_rating = page.query_selector('//span[@class="product-review__rating address-rate-mini address-rate-mini--sm"]').text_content()
            except(AttributeError):
                star_rating = False
                
            try:
                color = page.query_selector('//span[@class="color"]').text_content()
            except(AttributeError):
                color = False
            try:
                composition = page.query_selector('//p[@class="collapsable__content j-consist-popup"]').text_content().replace('Состав:', '')[41:]
            except(AttributeError):
                composition = False
                
            video_element = page.query_selector('//video[@class="wb-player__video j-wb-video-player"]')
            is_exist_video = not (video_element and not video_element.is_hidden())    
            
            list_of_pictures = operate_image(is_exist_video)
            list_to_return.append(name)
        
            data = {
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
            
            super_list.append(data)
        except(AttributeError) as e:
            logger.critical(f"Error {e} in url \n{url}")
            exit()
        
    # a = sql.check_product(data)
    # if not a : sql.insert_product(data)
    # print(a)
    

def parse_main_page(url_list = []):
    logger.debug("Parsing main page...")
    with open("url_list.txt", "r") as file:
        txt_urls = file.read().splitlines()
        
    skidka_link = "https://skidka7.com/discount/cwomen/all"
    page.goto(skidka_link)

    for current_page in range(1, 16):
        logger.info(f"Current page: {current_page}")
        url = f"{skidka_link}?page={current_page}"
        page.goto(url)
        cards = page.query_selector_all('//div[@class="col-xl-2 col-lg-2 col-md-3 col-sm-3 col-xs-6"]')
        for card in cards:
            sold_out_element = card.query_selector('//p[@style="color: red"]')
            sold_out = (sold_out_element and sold_out_element.is_visible())
            if sold_out: continue
            url = card.query_selector('//div[@class="panel panel-flat padding9"]/a[1]').get_attribute("href")
            if url in txt_urls:
                continue
            else:
                url_list.append(url)
    with open("url_list.txt", "w") as file:     
        for item in url_list:
            file.write(item + "," + "\n")
        
        
def initialize():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context()
        global page
        page = context.new_page()
        # wb_card_urls = parse_main_page()
        parse_wildberries()
        


if __name__ == "__main__":
    logger = logging.getLogger('WB')
    logger.setLevel(logging.DEBUG) # Установка уровня логирования
    handler = logging.StreamHandler() # Создание обработчика логов
    handler.setLevel(logging.DEBUG) # Установка уровня логирования для обработчика
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'green',
            'INFO':     'purple',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red',
        },
        secondary_log_colors={},
        style='%'
    )
    handler.setFormatter(formatter) # Создание форматтера и добавление его в обработчик
    logger.addHandler(handler) # Добавление обработчика в логгер
    initialize()
    logger.debug("Done")