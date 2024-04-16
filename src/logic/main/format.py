from aiogram.utils.markdown import hbold, hstrikethrough, hlink
from config import GOO_SO_TOKEN
import json
import requests
from random import choice


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
        short_url = f"https://goo.su/{self.__get_short_link(url)}"
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
