from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.markdown import hbold, hstrikethrough
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from aiogram.types import InputMediaPhoto
from configure_bot import TOKEN
import sql, tg_sql, ast, logging, json, os
from pprint import pprint
from main import initialize


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class SendPosts(StatesGroup):
    sender = State()
    wait_state = State()


def append_data_to_db(wb_id, status):
    post_exist = tg_sql.is_post_in_db(wb_id)
    if post_exist:
        tg_sql.set_post_status(wb_id=wb_id, status=status)
    elif post_exist == False:
        tg_sql.add_post(wb_id=wb_id, status=status)


def get_main_kb() -> types.ReplyKeyboardMarkup:
    main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_kb.add(
        types.KeyboardButton("Запостить"),
        types.KeyboardButton("Скип"),
    )
    return main_kb


def get_second_kb() -> types.ReplyKeyboardMarkup:
    ...


def wbparse():
    all_products = sql.get_all_products()
    tg_posts: list = tg_sql.get_all_posts()

    # wb_url = [product["url"] for product in all_products]
    filtered_products = [
        product for product in all_products if product["url"] not in tg_posts
    ]

    return filtered_products


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


def prepare_posts():
    try:
        posts_list: list = wbparse()
    except:
        return False
    for item in posts_list:
        posts_list.pop(0)
        url = item.get("url")
        wb_id = item.get("wb_id")
        is_in_db = tg_sql.is_post_in_db(url)
        post_status = tg_sql.get_post_status(url)
        if is_in_db and post_status in ["Liked", "Disliked"]:
            continue
        post, pic_url = format_post(item), item.get("pic_url")
        if len(pic_url) >= 80:
            pic_url = ast.literal_eval(pic_url)
        return post, pic_url, url


@dp.message_handler(state=SendPosts.sender)
async def sender(message: types.Message):
    global post_url
    try:
        post_text, pic_url, post_url = prepare_posts()
    except TypeError as e:
        await bot.send_message(message.chat.id, "Посты закончились")
        return
    except ValueError:
        post_text, pic_url, post_url = prepare_posts()
    await SendPosts.wait_state.set()
    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pic_url]
    pictures[0].caption = post_text
    await bot.send_media_group(chat_id=message.chat.id, media=pictures)
    return


@dp.message_handler(regexp="^[Зз]апостить|[Сс]кип$", state=SendPosts.wait_state)
async def post_or_skip(message: types.Message):
    user_message: str = message.text.lower()
    await SendPosts.sender.set()
    if user_message == "запостить":
        append_data_to_db(post_url, "Liked")
        await sender(message=message)
    elif user_message == "скип":
        append_data_to_db(post_url, "Disliked")
        await sender(message=message)


@dp.message_handler(commands=["clear"], state="*")
async def clear_tg_db(message: types.Message):
    try:
        tg_sql.close_connection()
        os.remove(tg_sql.db_file)
        await message.reply("БД с вб очищена")
        tg_sql.create_or_connect_database()
    except FileNotFoundError:
        await message.reply("Не могу найти файл")
        return
    except PermissionError:
        print("Закройте все процессы с БД!")
        await message.reply("Закройте все процессы с БД!")


@dp.message_handler(commands=["clear_wb"], state="*")
async def clear_wb_db(message: types.Message):
    try:
        sql.close_connection()
        os.remove(sql.db_file)
        await message.reply("БД с вб очищена")
        sql.create_or_connect_database()
    except FileNotFoundError:
        await message.reply("Не могу найти файл")
        return
    except PermissionError as e:
        print(e)
        print("Закройте все процессы с БД!")
        await message.reply("Закройте все процессы с БД!")


@dp.message_handler(commands=["parse"], state="*")
async def call_parser(message: types.Message):
    await bot.send_message(message.chat.id, text="Вызываю, подождите пару минут")
    # send gif
    await initialize()
    await bot.send_message(message.chat.id, text="Сделано")


@dp.message_handler(commands=["exit"], state="*")
async def leave_bot(message: types.Message):
    await message.reply("Завершаю работу")
    exit()


@dp.message_handler(commands=["start"], state="*")
async def start_point(message: types.Message):
    wbparse()
    await bot.send_message(
        message.chat.id, text="Высылаю посты", reply_markup=get_main_kb()
    )
    await sender(message=message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
