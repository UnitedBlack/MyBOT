from playwright.async_api import async_playwright
import asyncio

urls = [
    "https://www.wildberries.ru/catalog/162611650/detail.aspx",
    "https://www.wildberries.ru/catalog/154910940/detail.aspx",
    "https://www.wildberries.ru/catalog/176102403/detail.aspx",
    "https://www.wildberries.ru/catalog/172598431/detail.aspx",
    "https://www.wildberries.ru/catalog/166538326/detail.aspx",
    "https://www.wildberries.ru/catalog/163474322/detail.aspx",
    "https://www.wildberries.ru/catalog/168526465/detail.aspx",
    "https://www.wildberries.ru/catalog/186807840/detail.aspx",
    "https://www.wildberries.ru/catalog/172281236/detail.aspx",
    "https://www.wildberries.ru/catalog/180219196/detail.aspx",
    "https://www.wildberries.ru/catalog/170572157/detail.aspx",
]
#  'https://www.wildberries.ru/catalog/170505680/detail.aspx',
#  'https://www.wildberries.ru/catalog/172656111/detail.aspx',
#  'https://www.wildberries.ru/catalog/172767054/detail.aspx',
#  'https://www.wildberries.ru/catalog/172898901/detail.aspx',
#  'https://www.wildberries.ru/catalog/172895213/detail.aspx',
#  'https://www.wildberries.ru/catalog/160406565/detail.aspx',
#  'https://www.wildberries.ru/catalog/162470941/detail.aspx',
#  'https://www.wildberries.ru/catalog/183440434/detail.aspx',
#  'https://www.wildberries.ru/catalog/160147234/detail.aspx',
#  'https://www.wildberries.ru/catalog/126182096/detail.aspx',
#  'https://www.wildberries.ru/catalog/183636101/detail.aspx',
#  'https://www.wildberries.ru/catalog/183966557/detail.aspx',
#  'https://www.wildberries.ru/catalog/171248601/detail.aspx',
#  'https://www.wildberries.ru/catalog/117642437/detail.aspx',
#  'https://www.wildberries.ru/catalog/72374911/detail.aspx',
#  'https://www.wildberries.ru/catalog/147638769/detail.aspx',
#  'https://www.wildberries.ru/catalog/172579927/detail.aspx',
#  'https://www.wildberries.ru/catalog/172692015/detail.aspx',
#  'https://www.wildberries.ru/catalog/170570774/detail.aspx',
#  'https://www.wildberries.ru/catalog/170116438/detail.aspx']


async def load_page(browser, url):
    page = await browser.new_page()
    await page.goto(url)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        tasks = []
        for url in urls:
            task = asyncio.create_task(load_page(browser, url))
            tasks.append(task)
        await asyncio.gather(*tasks)
        await browser.close()

asyncio.run(main())