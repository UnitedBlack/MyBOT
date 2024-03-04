from aiogram import types, Router, F
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold
from prikol.weather import get_weather
from filters.admin_filter import IsAdmin
from database import service_db
import scheduler_app
from config import categories

start_menu_router = Router()
start_menu_router.message.filter(IsAdmin())


class StartMenuStates(StatesGroup):
    start = State()


@start_menu_router.message(StateFilter("*"), F.text == "Назад")
async def main_menu(message: types.Message):
    try:
        bd_count_text = f"В бд ВБ {hbold(service_db.count_of_products_in_db())} товаров"
        tgbd_count_text = (
            f"В бд ТГ {hbold(service_db.count_of_products_in_tgdb())} постов"
        )
        delay_count_text = (
            f"Постов в отложке {hbold(len(scheduler_app.get_delayed_posts(scheduler)))}"
        )
        await bot.send_message(
            admin_id,
            text=f"{hbold('Главное меню')}\n{bd_count_text}\n{tgbd_count_text}\n{delay_count_text}\n{get_weather()}",
            reply_markup=get_main_kb(),
            parse_mode="HTML",
        )
    except NameError:
        await start_point(message)


@start_menu_router.message(StateFilter("*"), F.text == "Категории")
@start_menu_router.message(StateFilter("*"), F.text == "Одежда тпшкам")
@start_menu_router.message(StateFilter("*"), F.text == "Для дома")
@start_menu_router.message(StateFilter("*"), F.text == "Бижутерия")
async def state_router(message: types.Message):
    global skidka_link, scheduler, chat_id, wb_table_name, tg_table_name
    config = categories.get(message.text)
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


@start_menu_router.message(CommandStart)
async def start_point(message: types.Message):
    await message.answer(text="Выберите категорию (канал)", reply_markup=get_start_kb())
