import formatter_app
import scheduler_app
import custom_scraper
import logging
from sql_data import posts_sql, products_sql
from scraper_app import main
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.markdown import hcode, hbold
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
    get_time_back_kb,
    get_custom_post_kb,
    get_edit_photo_kb,
    get_photo_editor_kb,
)
from ast import literal_eval
from configure_bot import (
    TOKEN,
    admin_id,
    categories_config,
)
from pprint import pprint
from preknown_errors import (
    playwright_random_error,
    tg_random_error,
    aiogram_wrong_string_length,
    failed_to_send_message,
    scheduler_not_defined,
    aiogram_badrequest
)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
user_pics = []


class States(StatesGroup):
    delayed_menu = State()
    delayed_delete = State()
    delayed_change = State()
    delayed_change_date = State()
    start = State()
    sender = State()
    wait_state = State()
    custom_post = State()
    custom_post_link = State()
    custom_post_menu = State()
    edit_description = State()
    edit_picture = State()
    clear_database = State()
    parser = State()
    clear_delayed = State()


def get_scrapy():
    global scrapy
    scrapy = formatter_app.Scrapy(
        skidka_link=skidka_link,
        wb_table_name=wb_table_name,
        tg_table_name=tg_table_name,
    )


@dp.errors_handler()
async def error_handler(update: types.Update, exception: Exception):
    await States.start.set()
    if str(exception) == scheduler_not_defined:
        await bot.send_message(admin_id, text="Забыл выбрать категорию")
        await start_point(update.message)
        return
    elif str(exception) == tg_random_error or str(exception) == failed_to_send_message:
        await bot.send_message(admin_id, text="Телеграм поносит, автоскипаю")
        await States.wait_state.set()
        await post_or_skip(update)
        return
    elif str(exception) == aiogram_wrong_string_length or str(exception) == aiogram_badrequest:
        await bot.send_message(admin_id, text="Аиограм поносит, нажмите кнопку скип")
        await States.wait_state.set()
        return
    elif str(exception) == playwright_random_error:
        return
    elif str(exception) == "NoneType' object has no attribute 'get":
        return
    else:
        await bot.send_message(admin_id, text=f"Не понятная мне ошибка\n{exception}")
        return


# CUSTOM POST MENU ============================================== CUSTOM POST MENU
@dp.message_handler(regexp="^Запостить$", state=States.custom_post_menu)
async def delay_custom_post(message: types.Message):
    custom_time = (
        calendar_hour,
        calendar_minute,
        calendar_day,
        calendar_month,
        calendar_year,
    )
    delay_data = {
        "post_text": post_text,
        "post_pic": pictures,
    }  # user_pics if user_pics else pics
    scheduler_app.schedule_post(delay_data, scheduler, ad=True, custom_time=custom_time)
    await bot.send_message(
        admin_id,
        text=f"Добавил в отложку, время {calendar_hour}:{calendar_minute} {calendar_day}-{calendar_month}",
    )
    await delayed_menu(message)


@dp.message_handler(state=States.edit_description)
async def edit_description(message: types.Message):
    await States.custom_post_menu.set()
    global post_text
    user_message = message.text
    post_text = user_message
    pictures[0].caption = user_message
    await bot.send_message(admin_id, text=f"Так будет выглядеть ваш пост:")
    await bot.send_media_group(chat_id=admin_id, media=pictures)


@dp.message_handler(regexp="^Редактировать описание$", state=States.custom_post_menu)
async def ask_edit_description(message: types.Message):
    await bot.send_message(
        admin_id,
        text=f"{post_text}\n\nВот текст поста, пришлите текст для редактирования",
        parse_mode="HTML",
    )
    await States.edit_description.set()


@dp.message_handler(regexp="^Выйти без сохранения$", state="*")
async def exit_without_saving(message: types.Message):
    await delayed_menu(message)


@dp.message_handler(content_types=["photo"], state=States.edit_picture)
async def edit_picture(message: types.Message):
    await bot.send_message(
        admin_id, "Сохранил. Ещё одну?", reply_markup=get_photo_editor_kb()
    )  # Клавиатуру типа "ВСЕ ХВАТИТ"
    user_pic = message.photo[-1].file_id  # Get the largest size of the photo
    user_pics.append(user_pic)  # Store the photo


@dp.message_handler(state=States.edit_picture)
async def process_pictures(message: types.Message):
    if message.text == "Закончить":
        global pictures
        pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in user_pics]
        pictures[0].caption = post_text
        await bot.send_media_group(chat_id=admin_id, media=pictures)
        user_pics.clear()  # Clear the list for the next set of photos
        await bot.send_message(
            admin_id, "Вот ваш пост", reply_markup=get_custom_post_kb()
        )
        await States.custom_post_menu.set()
    elif message.text == "Добавить фото":
        await bot.send_message(admin_id, "Присылайте по ОДНОЙ фотографии")
    elif message.text == "Удалить фото":
        ...


@dp.message_handler(regexp="^Редактировать фото$", state=States.custom_post_menu)
async def ask_edit_picture(message: types.Message):
    await States.edit_picture.set()
    await bot.send_message(
        admin_id, "Вы в редакторе фото", reply_markup=get_edit_photo_kb()
    )
    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pics]
    pictures[0].caption = "Это фотографии поста, как хотите изменить?"
    await bot.send_media_group(chat_id=admin_id, media=pictures)


@dp.message_handler(state=States.custom_post_link)
async def create_custom_post(message: types.Message):
    global post_text, pics, custom_data
    user_link = [message.text]
    await bot.send_message(
        admin_id, text="Вызываю парсер", reply_markup=get_custom_post_kb()
    )
    custom_data = await custom_scraper.main(user_link[0])
    post_text = scrapy.format_post(custom_data)
    pics = literal_eval(custom_data["pic_url"])
    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pics]
    pictures[0].caption = post_text
    await bot.send_media_group(chat_id=admin_id, media=pictures)
    await States.custom_post_menu.set()


# =======================================================================


# DAYVINCHIK ================================================== DAYVINCHIK
@dp.message_handler(state=States.sender)
async def sender(message: types.Message):
    global post_url, pic_url, post_text
    try:
        post_text, pic_url, post_url = scrapy.prepare_posts()
    except TypeError as e:
        if scrapy.count_of_products_in_db() < 1:
            await bot.send_message(admin_id, "БД с товарами пустая")
        elif scrapy.count_of_products_in_db == scrapy.count_of_products_in_tgdb:
            await bot.send_message(admin_id, "Закончились товары")
        else:
            await bot.send_message(admin_id, "Посты закончились или какая-то ошибка")

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
    try:
        user_message = message.text.lower()
    except AttributeError:
        user_message = "скип"
    await States.sender.set()
    if user_message == "запостить":
        delay_data = {"post_text": post_text, "post_pic": pic_url, "chat_id": chat_id}
        scheduler_app.schedule_post(delay_data, scheduler)
        scrapy.append_data_to_db(post_url, "Liked")
        await sender(message=message)

    elif user_message == "скип":
        scrapy.append_data_to_db(post_url, "Disliked")
        await sender(message=message)


# ==========================================================================


# MAIN MENU ATTRIBUTES ===================================== MAIN MENU ATTRIBUTES
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
    message_text = f"Вызываю парсер?\nСейчас в базе данных {scrapy.count_of_products_in_db()} товаров"
    await bot.send_message(admin_id, text=message_text, reply_markup=get_parser_kb())
    await States.parser.set()


@dp.message_handler(regexp="^Вызвать парсер$", state=States.parser, run_task=True)
async def call_parser(message: types.Message, state: FSMContext):
    await bot.send_message(
        admin_id,
        text="Вызвал, подождите пару минут.",
    )
    posts_num = await main(skidka_link, table_name=wb_table_name)
    await bot.send_message(admin_id, text=f"Сделано, число постов: {posts_num}")
    await main_menu(message)
    await state.finish()


# ================================================================================


# MAIN MENU ============================================================ MAIN MENU
@dp.message_handler(regexp="^Назад$", state="*")
async def main_menu(message: types.Message):
    try:
        bd_count_text = f"В бд ВБ {hbold(scrapy.count_of_products_in_db())} товаров"
        tgbd_count_text = f"В бд ТГ {hbold(scrapy.count_of_products_in_tgdb())} постов"
        delay_count_text = (
            f"Постов в отложке {hbold(len(scheduler_app.get_delayed_posts(scheduler)))}"
        )
        await bot.send_message(
            admin_id,
            text=f"{hbold('Главное меню')}\n{bd_count_text}\n{tgbd_count_text}\n{delay_count_text}\n{scrapy.get_weather()}",
            reply_markup=get_main_kb(),
            parse_mode="HTML",
        )
    except NameError:
        await start_point(message)


@dp.message_handler(regexp="^Категории|Одежда тпшкам|Для дома|Бижутерия$", state="*")
async def state_router(message: types.Message):
    global skidka_link, scheduler, chat_id, wb_table_name, tg_table_name
    config = categories_config.get(message.text)
    if config:
        skidka_link = config["skidka_link"]
        wb_table_name = config["wb_table_name"]
        tg_table_name = config["tg_table_name"]
        scheduler = config["scheduler"]
        chat_id = config["chat_id"]

        get_scrapy()
        await main_menu(message)
    elif message.text == "Категории":
        await start_point(message)
    else:
        await bot.send_message(admin_id, "Не работает")


@dp.message_handler(commands=["start"])
async def start_point(message: types.Message):
    await bot.send_message(
        chat_id=admin_id, text="Выберите категорию (канал)", reply_markup=get_start_kb()
    )


# ===============================================================================


# DELAYED MENU ===================================================== DELAYED MENU
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
            await States.custom_post.set()
            await send_calendar_inline_kb()
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
    year, month = datetime.now().year, datetime.now().month
    await bot.send_message(
        admin_id,
        f"📅Выберите день и время: ",
        reply_markup=create_calendar(
            year,
            month,
        ),
    )


@dp.message_handler(state=States.delayed_change_date)
async def change_post_delayed_time(message: types.Message):
    data = {
        "job_id": delayed_id,
        "custom_month": calendar_month,
        "custom_day": calendar_day,
        "custom_hour": calendar_hour,
        "custom_minute": calendar_minute,
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


# =============================================================================


# CLEAR DATABASE ================================================ CLEAR DATABASE
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


# ================================================================================


# CALLBACKS ============================================================ CALLBACKS
async def send_calendar_inline_kb():
    year, month = datetime.now().year, datetime.now().month
    await bot.send_message(
        admin_id,
        f"📅Выберите день и время: ",
        reply_markup=create_calendar(
            year,
            month,
        ),
    )


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith("prev-month"),
    state="*",
)
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


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith("next-month"),
    state="*",
)
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


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith("calendar"), state="*"
)
async def process_callback_calendar(callback_query: types.CallbackQuery):
    global calendar_day, calendar_month, calendar_year
    _, calendar_day, calendar_month, calendar_year = callback_query.data.split("-")
    await bot.edit_message_reply_markup(
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=create_time_kb(),
    )


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith("time"), state=States.delayed_change_date
)
async def process_callback_calendar_time(callback_query: types.CallbackQuery):
    global calendar_hour, calendar_minute
    _, calendar_hour, calendar_minute = callback_query.data.split("-")
    await change_post_delayed_time(message=callback_query.message)


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith("time"), state=States.custom_post
)
async def process_callback_calendar_time(callback_query: types.CallbackQuery):
    global calendar_hour, calendar_minute
    _, calendar_hour, calendar_minute = callback_query.data.split("-")
    await States.custom_post_link.set()
    await bot.delete_message(
        callback_query.from_user.id,
        callback_query.message.message_id,
    )
    await bot.send_message(
        admin_id,
        text=f"Выбранное время: {calendar_hour}:{calendar_minute} {calendar_day}-{calendar_month}\nПришлите ссылку на товар",
        reply_markup=get_time_back_kb(),
    )


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith("back-time"),
    state="*",
)
async def send_calendar_keyboard(callback_query: types.CallbackQuery):
    year, month = datetime.now().year, datetime.now().month
    await bot.edit_message_reply_markup(
        callback_query.from_user.id,
        callback_query.message.message_id,
        f"📅Выберите день и время: ",
        reply_markup=create_calendar(
            year,
            month,
        ),
    )


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith("change-time"),
    state="*",
)
async def change_inline_time(callback_query: types.CallbackQuery):
    await States.custom_post.set()
    year, month = datetime.now().year, datetime.now().month
    await bot.edit_message_reply_markup(
        callback_query.from_user.id,
        callback_query.message.message_id,
        f"📅Выберите день и время: ",
        reply_markup=create_calendar(
            year,
            month,
        ),
    )
    # await send_calendar_inline_kb()


# ==============================================================================

if __name__ == "__main__":
    executor.start_polling(dp)

# Фикс отложки, опять со временем проеб, доделать редактирование поста
# Мб добавить редактор в винчик
# сделать так что бы можно было в отложке выбирать время более гибко не топорно 21-00 21-30
# например, выберите час > выберите минуты
