from playwright.async_api import async_playwright
import asyncio
import sql
import time

super_list = []
index = 0

# async def operate_image(video):
#     picture_list = []
#     pic_count = await page.locator('//div[@class="sw-slider-kt-mix__wrap"]//ul[@class="swiper-wrapper"]/li').count()
#     base_pic_url = await page.query_selector('//img[@class="photo-zoom__preview j-zoom-image hide"]').get_attribute("src")
#     if video == False: pic_count += 1
#     for num in range(1, pic_count):
#         new_pic_url = base_pic_url.replace("1.webp", str(num)) + ".webp"
#         picture_list.append(new_pic_url)
#     return picture_list

# async def parse_wildberries(urls: list, list_to_return = []):
#     for url in urls:
#         await page.goto(url, wait_until='domcontentloaded')
#         await page.wait_for_selector('h1')
#         await asyncio.sleep(1)
        
#         try: 
#             sold_out = await page.query_selector('//span[@class="sold-out-product__text"]').is_visible()
#         except(AttributeError):
#             sold_out = False
            
#         if sold_out: continue
        
#         name = await page.query_selector("h1").text_content()
#         price = await page.query_selector('//ins[@class="price-block__final-price"]').text_content().replace(' ', '').replace('₽', '')
#         discount_price = await page.query_selector('//del[@class="price-block__old-price j-wba-card-item-show"]').text_content().replace(' ', '').replace('₽', '')
#         try:
#             star_rating = await page.query_selector('//span[@class="product-review__rating address-rate-mini address-rate-mini--sm"]').text_content()
#         except(AttributeError):
#             star_rating = False
            
#         try:
#             color = await page.query_selector('//span[@class="color"]').text_content()
#         except(AttributeError):
#             color = False
#         try:
#             composition = await page.query_selector('//p[@class="collapsable__content j-consist-popup"]').text_content().replace('Состав:', '')[41:]
#         except(AttributeError):
#             composition = False
            
#         video_element = await page.query_selector('//video[@class="wb-player__video j-wb-video-player"]')
#         is_exist_video = not (video_element and not await video_element.is_hidden())    
        
#         list_of_pictures = await operate_image(is_exist_video)
#         list_to_return.append(name)
    
#         data = {
#             "name": name,
#             "price": price,
#             "discount_price": discount_price,
#             "star_rating": star_rating,
#             "url": url,
#             "pic_url": str(list_of_pictures),
#             "composition": composition,
#             "size": "",
#             "color": color,
#             }
        
#         super_list.append(data)

async def parse_main_page(page, page_number):
    with open("url_list.txt", "r") as file:
        txt_urls = file.read().splitlines()
        
    skidka_link = "https://skidka7.com/discount/cwomen/all"
    await page.goto(skidka_link)
    
    elements = await page.query_selector_all('//ul[@class="pagination"]/li')
    page_count = int(await elements[-2].text_content()) + 1
    for current_page in range(1, page_count):
        url = f"{skidka_link}?page={current_page}"
        await page.goto(url)
        cards = await page.query_selector_all('//div[@class="col-xl-2 col-lg-2 col-md-3 col-sm-3 col-xs-6"]')
        tasks = []
        for card in cards:
            tasks.append(process_card(card, txt_urls))
        await asyncio.gather(*tasks)
    return url_list

async def process_card(card, txt_urls):
    sold_out_element = await card.query_selector('//p[@style="color: red"]')
    sold_out = (sold_out_element and await sold_out_element.is_visible())
    if sold_out: return
    element = await card.query_selector('//div[@class="panel panel-flat padding9"]/a[1]')
    url = await element.get_attribute("href")
    if url in txt_urls:
        return
    else:
        with open("url_list.txt", "a") as file:
            file.write(url + "," + "\n")
    
async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        context = await browser.new_context()
        pages = await asyncio.gather(*(context.new_page() for _ in range(5)))  # создаем 5 вкладок
        tasks = [parse_main_page(page, i+1) for i, page in enumerate(pages)]  # создаем задачи для каждой вкладки
        await asyncio.gather(*tasks)  # запускаем все задачи параллельно


asyncio.run(main())