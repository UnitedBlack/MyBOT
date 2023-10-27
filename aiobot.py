from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.markdown import hbold, hstrikethrough
from aiogram import types
from aiogram.types import InputMediaPhoto
from configure_bot import TOKEN
import sql, tg_sql, ast, logging, json


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def wbparse() -> list:
    global wbparse_result
    wbparse_result = sql.get_all_products()
    return None


def format_post(item):
    name = item.get("name")
    discount_price = item.get("discount_price")
    price = item.get("price")
    star_rating = item.get("star_rating")
    composition = item.get("composition")
    color = item.get("color")
    url = item.get("url")

    post = f"🎁 {hbold(name)}" if name else ""
    post += (
        f"\n💵Цена: {hstrikethrough(price)}₽ {hbold(discount_price)}₽"
        if price and discount_price
        else ""
    )
    post += f"\n🌟Рейтинг: {hbold(star_rating)}" if star_rating else ""
    post += f"\n🔬Состав: {hbold(composition)}" if composition else ""
    post += f"\n🌈Цвет: {hbold(color)}" if color else ""
    post += f"\n🔗Купить: {url}" if url else ""

    return post


# def prepare_posts():
#     try:
#         posts_list: list = wbparse_result
#     except:
#         return False
    
#     for item in posts_list:
#         wbparse_result.pop(0)
#         url = item.get("url")
#         wb_id = item.get("wb_id")

#         is_in_db = tg_sql.is_post_in_db(wb_id)
#         post_status = tg_sql.get_post_status(wb_id)
#         # print(post_status)
#         if is_in_db and post_status in ["Liked", "Disliked"]:
#             return "in_db"

#         post, pic_url = format_post(item), item.get("pic_url")
#         if len(pic_url) >= 80:
#             pic_url = ast.literal_eval(pic_url)

#         return post, pic_url, url

def prepare_posts():
    try:
        posts_list: list = wbparse_result
    except:
        return False
    
    for item in posts_list:
        wbparse_result.pop(0)
        url = item.get("url")
        wb_id = item.get("wb_id")

        is_in_db = tg_sql.is_post_in_db(url)
        post_status = tg_sql.get_post_status(url)
        print(post_status)
        if is_in_db and post_status in ["Liked", "Disliked"]:
            continue 

        post, pic_url = format_post(item), item.get("pic_url")
        if len(pic_url) >= 80:
            pic_url = ast.literal_eval(pic_url)

        return post, pic_url, url

async def sender(message: types.Message):
    try:
        post_text, pic_url, post_url = prepare_posts()
    except TypeError:
        await bot.send_message(message.chat.id, "Посты закончились")
        return
    except ValueError:
        post_text, pic_url, post_url = prepare_posts()

    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pic_url]
    pictures[0].caption = post_text
    await bot.send_media_group(chat_id=message.chat.id, media=pictures)
    return post_url


async def router(message: types.Message, user_message=""):
    if user_message.lower() == "запостить":
        to_post = await sender(message=message)
        post_exist = tg_sql.is_post_in_db(to_post)
        print(post_exist)
        if post_exist:
            tg_sql.set_post_status(wb_id=to_post, status="Liked")
        elif post_exist == False:
            tg_sql.add_post(wb_id=to_post, status="Liked")
        return to_post

    elif user_message.lower() == "скип":
        to_post = await sender(message=message)
    elif (
        user_message.lower() != "запостить" or user_message.lower() != "скип"
    ):  # from start_point
        from_start_to_post = await sender(message=message)
        return from_start_to_post

@dp.message_handler(commands=["clear"])
async def clear_db(message: types.Message):
    await tg_sql.clear_sql()
    await bot.send_message(chat_id=message.chat.id, text="БД очищена")


@dp.message_handler(regexp="^[Зз]апостить|[Сс]кип$")
async def post_or_skip(message: types.Message):
    if message.text.lower() == "запостить":
        await router(message=message, user_message="запостить")
    elif message.text.lower() == "скип":
        await router(message=message, user_message="скип")


@dp.message_handler(commands=["start"])
async def start_point(message: types.Message):
    main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_kb.add(types.KeyboardButton("Запостить"), types.KeyboardButton("Скип"))
    wbparse()
    if wbparse:
        await bot.send_message(message.chat.id, "Высылаю посты.", reply_markup=main_kb)
        await router(message=message)
    elif wbparse is False:
        pass


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
