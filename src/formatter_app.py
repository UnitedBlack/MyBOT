from aiogram.utils.markdown import hbold, hstrikethrough, hlink
from configure_bot import GOO_SO_TOKEN
import ast, json
from sql_data import posts_sql, products_sql
import requests
from random import choice
from pprint import pprint


class Scrapy:
    def __init__(
        self,
        skidka_link,
        wb_table_name,
        tg_table_name,
    ):
        self.skidka_link = skidka_link
        self.wb_table_name = wb_table_name
        self.tg_table_name = tg_table_name

    def get_short_link(self, link):
        result = requests.post(
            url="https://goo.su/api/links/create",
            headers={
                "content-type": "application/json",
                "x-goo-api-token": GOO_SO_TOKEN,
            },
            data=json.dumps({"url": link}),
        )
        if result.status_code == 200:
            return json.loads(result.text)["link"]["short"]

    def append_data_to_db(self, wb_id, status):
        post_exist = posts_sql.is_post_in_db(wb_id, self.tg_table_name)
        if post_exist:
            posts_sql.set_post_status(
                wb_id=wb_id,
                status=status,
                table_name=self.tg_table_name,
            )
        elif post_exist == False:
            posts_sql.add_post(
                wb_id=wb_id,
                status=status,
                table_name=self.tg_table_name,
            )

    def wbparse(self):
        all_products = products_sql.get_all_products(self.wb_table_name)

        tg_posts = posts_sql.get_all_posts(self.tg_table_name)
        filtered_products = [
            product for product in all_products if product["url"] not in tg_posts
        ]
        return filtered_products

    def format_post(self, item):
        try:
            name = item.get("name")
        except AttributeError:
            name = item.get("name")
        discount_price = item.get("discount_price")
        price = item.get("price")
        star_rating = item.get("star_rating")
        composition = item.get("composition")
        color = item.get("color")
        url = item.get("url")
        discount_percent = ((int(price) - int(discount_price)) / int(price)) * 100
        try:
            short_url = f"https://goo.su/{self.get_short_link(url)}"
        except:
            short_url = False
        title_emoji = choice(["♨️", "💯", "🔎", "📌", "🎈", "💥", "⚡️"])
        price_emoji = choice(["💸", "💰", "💵"])
        post = f"{title_emoji}{hbold(name)}" if name else ""
        post += (
            f"\n\n{price_emoji}Цена: {hstrikethrough(price)}₽ {hbold(discount_price)}₽ (скидка {hbold(int(discount_percent))}%)"
            if price and discount_price
            else ""
        )
        if float(star_rating) >= 4.8:
            post += (
                f"\n\n⭐️{hbold('Хороший рейтинг')}: {hbold(star_rating)}"
                if star_rating
                else ""
            )
        else:
            post += f"\n\n🌟Рейтинг: {hbold(star_rating)}" if star_rating else ""

        post += f"\n\n🔬Состав: {hbold(composition)}" if composition else ""
        post += f"\n\n🌈Цвет: {hbold(color)}" if color else ""
        post += (
            f"\n\n🔗{hbold('Купить здесь:')} {hlink(url=short_url, title='ссылка на товар')}"
            if short_url
            else url
        )

        return post

    def prepare_posts(self):
        try:
            posts_list: list = self.wbparse()
        except:
            return False
        
        for item in posts_list:
            posts_list.pop(0)
            url = item.get("url")
            wb_id = item.get("wb_id")
            is_in_db = posts_sql.is_post_in_db(url, self.tg_table_name)
            post_status = posts_sql.get_post_status(url, self.tg_table_name)
            if is_in_db and post_status in ["Liked", "Disliked"]:
                continue
            post, pic_url = self.format_post(item), item.get("pic_url")
            if len(pic_url) >= 80:
                pic_url = ast.literal_eval(pic_url)
            return post, pic_url, url

    def count_of_products_in_db(self):
        return len(products_sql.get_all_products(self.wb_table_name))

    def count_of_products_in_tgdb(self):
        return len(posts_sql.get_all_posts(self.tg_table_name))

    def get_weather(self, api_key="e8c4e195e035f4befb6d2f044b5cfcc5", city="Москва"):
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        )
        data = response.json()
        main_data = data["main"]
        temperature = round(main_data["temp"])
        feels_like = f"{round(main_data['feels_like'])}°C"
        humidity = main_data["humidity"]
        data_to_return = f"В Москве {temperature}°C, по ощущениям {feels_like}"
        data_to_return += (
            f", на улице слызько" if int(humidity) > 75 else f", на улице сухо и мерзко"
        )
        return data_to_return
