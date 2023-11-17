import parser_app
import scheduler_app
import logging
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from sql_data import posts_sql, products_sql
from main import main
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.markdown import hcode
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from aiogram.types import InputMediaPhoto
from keyboards import (
    get_clear_db_kb,
    get_main_kb,
    get_parser_kb,
    get_second_kb,
    get_start_kb,
    get_third_kb,
    get_approve_kb,
    create_calendar,
    create_time_kb,
)
from apscheduler.schedulers.background import BackgroundScheduler
from ast import literal_eval
from configure_bot import (
    TOKEN,
    admin_id,
    tp_group_id,
    home_group_id,
    bijou_group_id,
    jobstores_tp,
    jobstores_home,
    jobstores_bijou,
)
from pprint import pprint
from preknown_errors import (
    playwright_random_error,
    scrapy_error,
    tg_random_error,
    aiogram_wrong_string_length,
)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class States(StatesGroup):
    delayed_menu = State()
    delayed_delete = State()
    delayed_change = State()
    delayed_change_date = State()
    start = State()
    sender = State()
    wait_state = State()
    custom_post = State()
    clear_database = State()
    parser = State()
    clear_delayed = State()


def get_scrapy():
    global scrapy
    scrapy = parser_app.Scrapy(
        skidka_link=skidka_link,
        wb_table_name=wb_table_name,
        tg_table_name=tg_table_name,
    )


@dp.errors_handler()
async def error_handler(update: types.Update, exception: Exception):
    await States.start.set()
    if str(exception) == scrapy_error:
        await bot.send_message(admin_id, text="Забыл выбрать категорию")
        return
    elif str(exception) == tg_random_error:
        await bot.send_message(admin_id, text="Телеграм поносит, нажмите кнопку скип")
        await States.wait_state.set()
        return
    elif str(exception) == aiogram_wrong_string_length:
        await bot.send_message(admin_id, text="Аиограм поносит, нажмите кнопку скип")
        await States.wait_state.set()
        return
    elif str(exception) == playwright_random_error:
        pass
    elif str(exception) == "NoneType' object has no attribute 'get":
        pass
    else:
        await bot.send_message(admin_id, text=f"Не понятная мне ошибка\n{exception}")
        return
    return


@dp.message_handler(state=States.custom_post)
async def create_custom_post(message: types.Message):
    user_link = [message.text]
    if message.text == "Назад":
        return
    data = await main(
        link=list(user_link),
        custom=True,
        table_name=wb_table_name,
    )  # обработка если уже в бд
    post_text = scrapy.format_post(data)
    pics = literal_eval(data["pic_url"])
    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pics]
    pictures[0].caption = post_text
    await bot.send_media_group(chat_id=admin_id, media=pictures)
    delay_data = {"post_text": post_text, "post_pic": pics}
    scheduler_app.schedule_post(delay_data, scheduler, ad=True)
    bot.send_message(admin_id, text="Отправил в отложку")
    await delayed_menu(message)


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
    except ValueError as e:
        post_text, pic_url, post_url = scrapy.prepare_posts()
        print(e)
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
        delay_data = {"post_text": post_text, "post_pic": pic_url, "chat_id": chat_id}
        scheduler_app.schedule_post(delay_data, scheduler)
        scrapy.append_data_to_db(post_url, "Liked")
        await sender(message=message)

    elif user_message == "скип":
        scrapy.append_data_to_db(post_url, "Disliked")
        await sender(message=message)


@dp.message_handler(regexp="^Листать посты$", state="*")
async def select_posts(message: types.Message):
    await States.sender.set()
    # scrapy.wbparse()
    await message.reply("Высылаю посты", reply_markup=get_second_kb())
    await sender(message=message)


@dp.message_handler(regexp="^Отложка$", state="*")
async def delayed_menu(message: types.Message):
    await States.delayed_menu.set()
    delayed_post = scheduler_app.get_delayed_posts(scheduler)
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
        await bot.send_message(
            admin_id, text="Отложка пустая", reply_markup=get_third_kb()
        )


@dp.message_handler(regexp="^Парсер$", state="*")
async def ask_for_parser(message: types.Message):
    message_text = f"Вызываю парсер?\nСейчас в базе данных {scrapy.count_of_products_in_db()} продуктов"
    await bot.send_message(admin_id, text=message_text, reply_markup=get_parser_kb())
    await States.parser.set()


@dp.message_handler(regexp="^Вызвать парсер$", state=States.parser)
async def call_parser(message: types.Message, state: FSMContext):
    await bot.send_message(
        admin_id,
        text="Вызываю, подождите пару минут. Рекомендую /clear_wb или /clear чтобы очистить БД",
    )
    posts_num = await main(skidka_link, table_name=wb_table_name)
    await bot.send_message(admin_id, text=f"Сделано, число постов: {posts_num}")
    await state.finish()


@dp.message_handler(regexp="^Назад$", state="*")
async def main_menu(message: types.Message):
    try:
        bd_count_text = f"В бд ВБ {scrapy.count_of_products_in_db()} продуктов"
        tgbd_count_text = f"В бд ТГ {scrapy.count_of_products_in_tgdb()} постов"
        delay_count_text = (
            f"Постов в отложке {len(scheduler_app.get_delayed_posts(scheduler))}"
        )
        await bot.send_message(
            admin_id,
            text=f"*Главное меню*\n{bd_count_text}\n{tgbd_count_text}\n{delay_count_text}\n{scrapy.get_weather()}",
            reply_markup=get_main_kb(),
        )
    except NameError:
        await start_point()


@dp.message_handler(
    regexp="^Категории|Одежда тпшкам|Для дома|Бижутерия|Косметика$", state="*"
)
async def state_router(message: types.Message):
    global skidka_link, scheduler, chat_id, wb_table_name, tg_table_name
    match message.text:
        case "Одежда тпшкам":
            skidka_link = "https://skidka7.com/discount/cwomen/all"
            wb_table_name = "tp_wb"
            tg_table_name = "tp_tg"
            scheduler = schedulerTP
            skidka_link = "https://skidka7.com/discount/cwomen/all"
            chat_id = tp_group_id
        case "Для дома":
            skidka_link = "https://skidka7.com/discount/dom/all"
            wb_table_name = "home_wb"
            tg_table_name = "home_tg"
            scheduler = schedulerHome
            chat_id = home_group_id
        case "Бижутерия":
            skidka_link = "https://skidka7.com/discount/jew/all"
            wb_table_name = "bijou_wb"
            tg_table_name = "bijou_tg"
            scheduler = schedulerBijou
            chat_id = bijou_group_id
        case "Категории":
            await start_point()
            return
        case _:
            await bot.send_message(admin_id, "Не работает")
            return

    get_scrapy()
    await main_menu(message)


@dp.message_handler(
    regexp="^Удалить пост|Изменить время|Кастомный пост|Очистить всю отложку$",
    state=States.delayed_menu,
)
async def ask_delayed_id(message: types.Message):
    match message.text:
        case "Удалить пост":
            await States.delayed_delete.set()
            await bot.send_message(message.chat.id, text="Пришлите ID отложки")

        case "Изменить время":
            await States.delayed_change.set()
            await bot.send_message(
                message.chat.id,
                text="Пришлите ID отложки'",
            )
        case "Кастомный пост":
            await bot.send_message(
                chat_id=admin_id,
                text="Пришлите ссылку на товар или несколько ссылок, разделенные запятой",
            )
            await States.custom_post.set()
        case "Очистить всю отложку":
            await bot.send_message(
                chat_id=admin_id,
                text="Вы уверены, что хотите удалить ВСЕ отложенные посты?",
                reply_markup=get_approve_kb(),
            )
            await States.clear_delayed.set()


@dp.message_handler(regexp="^Да$", state=States.clear_delayed)
async def clear_delayed_posts(message: types.Message):
    scheduler_app.remove_all_jobs(scheduler)
    await bot.send_message(admin_id, "Удалил все посты из отложки")
    await delayed_menu(message)


@dp.message_handler(state=States.delayed_change)
async def get_delayed_id(message: types.Message):
    global delayed_id
    await States.delayed_change_date.set()
    delayed_id = message.text
    await bot.send_message(
        admin_id, text=f"📅Выберите день: ", reply_markup=create_calendar
    )


@dp.message_handler(state=States.delayed_change_date)
async def change_post_delayed_time(
    message: types.Message, callback_query: types.CallbackQuery
):
    _, day, month, year = callback_query.data.split("-")
    # delayed_id, user_date = message.text.splitlines()
    # formatted_date = datetime.strptime(str(user_date), "%d-%m %H:%M")
    data = {
        "job_id": delayed_id,
        "custom_month": month,
        "custom_day": day,
        # "custom_hour": formatted_date.hour,
        # "custom_minute": formatted_date.minute,
    }
    scheduler_app.reschedule_post(data, scheduler)
    await message.reply("Изменил")
    await delayed_menu(message)


@dp.message_handler(state=States.delayed_delete)
async def delete_delayed_post(message: types.Message, state: FSMContext):
    delayed_id = message.text
    scheduler_app.delete_job(delayed_id, scheduler)
    await state.finish()
    await delayed_menu(message)


@dp.message_handler(regexp="^Очистить ТГ БД$", state=States.clear_database)
async def clear_tg(message: types.Message):
    posts_sql.delete_all_records(tg_table_name)
    await message.reply("Очистил")
    get_scrapy()


@dp.message_handler(regexp="^Очистить ВБ БД$", state=States.clear_database)
async def clear_wb(message: types.Message):
    products_sql.delete_all_records(wb_table_name)
    await message.reply("Очистил")
    get_scrapy()


@dp.message_handler(regexp="^Очистка БД$", state="*")
async def clear_db(message: types.Message):
    await bot.send_message(
        admin_id, text="Какую бд хотите очистить?", reply_markup=get_clear_db_kb()
    )
    await States.clear_database.set()


@dp.message_handler(commands=["start"])
async def start_point(message: types.Message):
    # await bot.send_message(
    #     chat_id=admin_id, text="Выберите категорию (канал)", reply_markup=get_start_kb()
    # )
    year, month = datetime.now().year, datetime.now().month
    await bot.send_message(
        message.chat.id,
        f"📅Выберите день и время: ",
        reply_markup=create_calendar(
            year,
            month,
        ),
    )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("prev-month"))
async def process_callback_prev_month(callback_query: types.CallbackQuery):
    _, month, _, year = callback_query.data.split("-")[1:]
    month, year = int(month), int(year)
    month -= 1
    if month < 1:
        month = 12
        year -= 1
    markup = create_calendar(year, month)
    await bot.edit_message_text(
        "📅Выберите день и время: ",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=markup,
    )
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("next-month"))
async def process_callback_next_month(callback_query: types.CallbackQuery):
    _, month, _, year = callback_query.data.split("-")[1:]
    month, year = int(month), int(year)
    month += 1
    if month > 12:
        month = 1
        year += 1
    markup = create_calendar(year, month)
    await bot.edit_message_text(
        "📅Выберите день и время: ",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=markup,
    )
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("calendar"))
async def process_callback_calendar(callback_query: types.CallbackQuery):
    global calendar_day, calendar_month, calendar_year
    _, calendar_day, calendar_month, calendar_year = callback_query.data.split("-")
    await bot.edit_message_reply_markup(
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=create_time_kb(),
    )


if __name__ == "__main__":
    schedulerTP = BackgroundScheduler(jobstores=jobstores_tp)
    schedulerHome = BackgroundScheduler(jobstores=jobstores_home)
    schedulerBijou = BackgroundScheduler(jobstores=jobstores_bijou)
    schedulerTP.start()
    schedulerHome.start()
    schedulerBijou.start()
    executor.start_polling(dp, skip_updates=True)


# @dp.callback_query_handler(
#     lambda c: c.data and c.data.startswith("calendar-"), state=States.delayed_change
# )
# async def process_callback_selected_day(callback_query: types.CallbackQuery):
#     _, day, month, year = callback_query.data.split("-")
#     print(f"{day}-{month}-{year}")
#     print(callback_query.data)
