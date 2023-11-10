from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.markdown import hcode
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from aiogram.types import InputMediaPhoto
from configure_bot import (
    TOKEN,
    admin_id,
    tp_group_id,
    home_group_id,
    bijou_group_id,
)
import sql, tg_sql
from pprint import pprint
from main import main
from keyboards import get_start_kb, get_main_kb, get_second_kb, get_third_kb
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from path_to_db import (
    tp_wb,
    tp_tgwb,
    home_wb,
    home_tgwb,
    bijou_wb,
    bijou_tgwb,
)
import parser_app

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class States(StatesGroup):
    delayed_menu = State()
    delayed_delete = State()
    delayed_change = State()
    start = State()
    sender = State()
    wait_state = State()
    get_channel = State()


@dp.message_handler(state=States.sender)
async def sender(message: types.Message):
    global post_url, pic_url, post_text
    try:
        post_text, pic_url, post_url = scrapy.prepare_posts()
    except TypeError as e:
        await bot.send_message(admin_id, "Посты закончились или какая-то ошибка")
        await bot.send_message(admin_id, e)
        await States.start.set()
        await main_menu(message)
        return
    except ValueError:
        post_text, pic_url, post_url = scrapy.prepare_posts()
    await States.wait_state.set()
    global pictures
    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pic_url]
    pictures[0].caption = post_text
    await bot.send_media_group(chat_id=admin_id, media=pictures)
    return


@dp.message_handler(
    regexp="^[Зз]апостить|[Сс]кип$",
    state=States.wait_state,
)
async def post_or_skip(message: types.Message):
    user_message: str = message.text.lower()
    await States.sender.set()
    if user_message == "запостить":
        delay_data = {"post_text": post_text, "post_pic": pic_url}
        status = scrapy.schedule_post(delay_data)
        scrapy.append_data_to_db(post_url, "Liked")
        await sender(message=message)

    elif user_message == "скип":
        scrapy.append_data_to_db(post_url, "Disliked")
        await sender(message=message)


@dp.message_handler(regexp="^Листать посты$", state="*")
async def select_posts(message: types.Message):
    await States.sender.set()
    await message.reply("Высылаю посты", reply_markup=get_second_kb())
    await sender(message=message)


@dp.message_handler(regexp="^Отложка$", state="*")
async def get_delayed_posts(message: types.Message):
    await States.delayed_menu.set()
    delayed_post = scrapy.get_delayed_posts()

    if delayed_post:
        delayed_posts = ""
        for delayed in delayed_post:
            jobname = delayed["jobname"]
            jobtime = delayed["jobtime"]
            jobid = delayed["job_id"]
            delayed_posts += f"{jobname}\n{jobtime}\n{hcode(jobid)}\n{'='*32}\n"

        await bot.send_message(
            admin_id,
            text=delayed_posts,
            parse_mode="HTML",
            reply_markup=get_third_kb(),
        )
    elif delayed_post == []:
        await bot.send_message(admin_id, text="Отложка пустая")


@dp.message_handler(regexp="^Парсер$", state="*")
async def call_parser(message: types.Message):
    await bot.send_message(
        admin_id,
        text="Вызываю, подождите пару минут. Рекомендую /clear_wb или /clear чтобы очистить БД",
    )
    posts_num = await main(skidka_link, connection_wb)
    await bot.send_message(admin_id, text=f"Сделано, число постов: {posts_num}")


@dp.message_handler(regexp="^Назад$", state="*")
async def main_menu(message: types.Message):
    await bot.send_message(
        admin_id, text="Вы в главном меню", reply_markup=get_main_kb()
    )


@dp.message_handler(
    regexp="^Категории|Одежда тпшкам|Для дома|Бижутерия|Косметика$", state="*"
)
async def state_router(message: types.Message):
    global connection_wb, connection_tg, skidka_link, scrapy
    match message.text:
        case "Одежда тпшкам":
            skidka_link = "https://skidka7.com/discount/cwomen/all"
            database_file_wb = tp_wb
            database_file_tg = tp_tgwb
            connection_wb = sql.connect_database(db_file=database_file_wb)
            connection_tg = tg_sql.connect_database(db_file=database_file_tg)
            scheduler = schedulerTP
            skidka_link = "https://skidka7.com/discount/cwomen/all"
            chat_id = tp_group_id
        case "Для дома":
            skidka_link = "https://skidka7.com/discount/dom/all"
            database_file_wb = home_wb
            database_file_tg = home_tgwb
            connection_wb = sql.connect_database(db_file=database_file_wb)
            connection_tg = tg_sql.connect_database(db_file=database_file_tg)
            scheduler = schedulerHome
            chat_id = home_group_id
        case "Бижутерия":
            skidka_link = "https://skidka7.com/discount/jew/all"
            database_file_wb = bijou_wb
            database_file_tg = bijou_tgwb
            connection_wb = sql.connect_database(db_file=database_file_wb)
            connection_tg = tg_sql.connect_database(db_file=database_file_tg)
            scheduler = schedulerBijou
            chat_id = (bijou_group_id,)
        case "Категории":
            await start_point(message)
            return
        case _:
            await bot.send_message(admin_id, "Не работает")
            return
    scrapy = parser_app.Scrapy(
        skidka_link=skidka_link,
        wb_db=database_file_wb,
        tg_db=database_file_tg,
        connection_wb=connection_wb,
        connection_tg=connection_tg,
        scheduler=scheduler,
        chat_id=chat_id,
    )
    scrapy.wbparse()
    await main_menu(message)


@dp.message_handler(regexp="^Удалить пост|Изменить время$", state=States.delayed_menu)
async def ask_delayed_id(message: types.Message):
    if message.text == "Удалить пост":
        await States.delayed_delete.set()
        await bot.send_message(message.chat.id, text="Пришлите ID отложки")

    elif message.text == "Изменить время":
        await States.delayed_change.set()
        await bot.send_message(
            message.chat.id,
            text="Пришлите ID отложки и время в формате '31(д)-10(м) 10:15'",
        )


@dp.message_handler(state=States.delayed_change)
async def change_post_delayed_time(message: types.Message):
    delayed_id, user_date = message.text.splitlines()
    formatted_date = datetime.strptime(str(user_date), "%d-%m %H:%M")
    data = {
        "job_id": delayed_id,
        "custom_month": formatted_date.month,
        "custom_day": formatted_date.day,
        "custom_hour": formatted_date.hour,
        "custom_minute": formatted_date.minute,
    }
    scrapy.reschedule_post(data)
    await message.reply("Изменил")
    await get_delayed_posts(message)


@dp.message_handler(state=States.delayed_delete)
async def delete_delayed_post(message: types.Message, state: FSMContext):
    delayed_id = message.text
    scrapy.delete_job(delayed_id)
    await state.finish()
    await get_delayed_posts(message)


@dp.message_handler(commands=["clear"], state="*")
async def clear_tg(message: types.Message):
    sql.close_connection(connection_tg)
    scrapy.clear_tg()
    await message.reply("Очистил")


@dp.message_handler(commands=["clear_wb"], state="*")
async def clear_wb(message: types.Message):
    sql.close_connection(connection_wb)
    scrapy.clear_wb()
    await message.reply("Очистил")


@dp.message_handler(commands=["start"])
async def start_point(message: types.Message):
    await bot.send_message(
        chat_id=admin_id, text="Выберите категорию (канал)", reply_markup=get_start_kb()
    )


if __name__ == "__main__":
    schedulerTP = BackgroundScheduler()
    schedulerHome = BackgroundScheduler()
    schedulerBijou = BackgroundScheduler()
    schedulerTP.start()
    schedulerHome.start()
    schedulerBijou.start()
    executor.start_polling(dp, skip_updates=True)
