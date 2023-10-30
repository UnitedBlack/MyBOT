from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.markdown import hbold, hstrikethrough
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from aiogram.types import InputMediaPhoto
from configure_bot import TOKEN
import sql, tg_sql, ast, logging, json, os, asyncio
from pprint import pprint
from main import initialize
import requests


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
headers = {"Content-Type": "application/json"}


class SendPosts(StatesGroup):
    start = State()
    sender = State()
    wait_state = State()


def schedule_post(data, message: types.Message):
    result = requests.post(
        # url="https://inlinegptbot.unitedblack.repl.co",
        url="http://127.0.0.1:80",
        data=json.dumps(data),
        headers=headers,
    )

    return result.status_code


def request_delayed_posts():
    data = {"get_delayed_posts": "get_delayed_posts"}
    result = requests.post(
        # url="https://inlinegptbot.unitedblack.repl.co",
        url="http://127.0.0.1:80",
        data=json.dumps(data),
        headers=headers,
    )
    return result.text


def request_change_time():
    ...


def request_delete_delayed():
    ...


def append_data_to_db(wb_id, status):
    post_exist = tg_sql.is_post_in_db(wb_id)
    if post_exist:
        tg_sql.set_post_status(wb_id=wb_id, status=status)
    elif post_exist == False:
        tg_sql.add_post(wb_id=wb_id, status=status)


def get_second_kb() -> types.ReplyKeyboardMarkup:
    second_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    second_kb.add(
        types.KeyboardButton("Запостить"),
        types.KeyboardButton("Скип"),
        types.KeyboardButton("Назад"),
    )
    return second_kb


def get_main_kb() -> types.ReplyKeyboardMarkup:
    main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_kb.add(
        types.KeyboardButton("Листать посты"),
        types.KeyboardButton("Получить список отложек"),
        types.KeyboardButton("Изменить время отложки"),
        types.KeyboardButton("Удалить пост из отложки"),
    )
    return main_kb


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


async def poster():
    ...


@dp.message_handler(state=SendPosts.sender)
async def sender(message: types.Message):
    global post_url, pic_url, post_text
    try:
        post_text, pic_url, post_url = prepare_posts()
    except TypeError as e:
        await bot.send_message(message.chat.id, "Посты закончились")
        return
    except ValueError:
        post_text, pic_url, post_url = prepare_posts()
    await SendPosts.wait_state.set()
    global pictures
    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pic_url]
    pictures[0].caption = post_text
    await bot.send_media_group(chat_id=message.chat.id, media=pictures)
    return


@dp.message_handler(regexp="^[Зз]апостить|[Сс]кип$", state=SendPosts.wait_state)
async def post_or_skip(message: types.Message):
    user_message: str = message.text.lower()
    await SendPosts.sender.set()
    if user_message == "запостить":
        delay_data = {"post_text": post_text, "post_pic": pic_url}
        status = schedule_post(delay_data, message)

        if status != 200:
            await message.reply("Произошла ошибка с отложкой поста")
        else:
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
        await message.reply("БД с тг очищена")
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


@dp.message_handler(commands=["delayed"], state="*")
async def show_delayed_posts(message: types.Message):
    ...


@dp.message_handler(commands=["exit"], state="*")
async def leave_bot(message: types.Message):
    await message.reply("Завершаю работу")
    exit()


@dp.message_handler(regexp="^Назад$", state="*")
async def main_menu(message: types.Message):
    # await SendPosts.start.set()
    await bot.send_message(
        message.chat.id, text="Вы в главном меню", reply_markup=get_main_kb()
    )


@dp.message_handler(regexp="^Листать посты$", state="*")
async def select_posts(message: types.Message):
    # await SendPosts.sender.set()
    await message.reply("Высылаю посты", reply_markup=get_second_kb())
    await sender(message=message)


@dp.message_handler(regexp="^Получить список отложек$", state="*")
async def get_delayed_posts(message: types.Message):
    delayed_post = json.loads(request_delayed_posts())["delayed_posts"]
    for delayed in delayed_post:
        jobname = delayed["jobname"]
        jobtime = delayed["jobtime"]
        jobid = delayed["job_id"]
        msg = f"{jobname}\n{jobtime}\n<code>{jobid}</code>"
        await bot.send_message(message.chat.id, text=msg, parse_mode='HTML')
        await asyncio.sleep(1)

# Оставить только кнопку получить список отложек
# После нажатия на нее и рассылки всех сообщений выводить "изменить время отложки" и "удалить" и "назад"
# а еще сделать чтобы отложка выводилась одним сообщением
# {'delayed_posts': [{'job_id': 'af14896b133b4f80bb37817eb938a652', 'jobname': 'Набор ярких длинных носков 5 пар', 'jobtime': '31-10 03:00'}, {'job_id': 'ad1d0cd0991141cc9e6c57836a5c27d3', 'jobname': 'Носки теплые набор махровые Термоноски', 'jobtime': '31-10 04:00'}, {'job_id': '9c10c', 'jobname': 'Набор ярких носков 10 пар', 'jobtime': '31-10 06:00'}, {'job_id': '6902cb11cf464b858cba8d44a77fa414', 'jobname': 'Топ спортивный на бретелях', 'jobtime': '31-10 07:00'}, {'job_id': '34518811df46475b815d4b9441e8956d', 'jobname': 'Пуховик зимний длинный с капюшоном', 'jobtime': '31-10 08:00'}, {'job_id': '8f84cc27275a4530b8694bb9d9a5b1dd', 'jobname': 'Пиджак укороченный теплый  блейзер  базовый', 'jobtime': '31-10 09:00'}, {'job_id': '009a6457596447298396293050cc54ad', 'jobname': 'Джинсы клеш трубы', 'jobtime': '31-10 10:00'}, {'job_id': 'a129d7ac33e04d13be928598404b1863', 'jobname': 'Костюм домашний с брюками и топом', 'jobtime': '31-10 11:00'}, {'job_id': '3d47003029af4b8ea2f1fa1308e2ade4', 'jobname': 'Сумка Дорожная Ручная кладь Для фитнеса Спортивная Шоппер', 'jobtime': '31-10 12:00'}, {'job_id': 'ccc1a7e10fcc429eaca125e8ad9feafb', 'jobname': 'Тапочки домашние меховые', 'jobtime': '31-10 13:00'}]}


@dp.message_handler(commands=["start"], state="*")
async def start_point(message: types.Message):
    wbparse()
    await main_menu(message)
    # await sender(message=message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
