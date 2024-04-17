import scheduler_app
from aiogram import types, Router, F
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold
from logic.prikol.weather import get_weather
from filters.admin_filter import IsAdmin
from config import categories
from keyboards.reply import get_keyboard
from logic.main.core import ScrapyCore
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Products, Posts

start_menu_router = Router()
start_menu_router.message.filter(IsAdmin())

class StartMenuStates(StatesGroup):
    start = State()

def get_scrapy(skidka_category_link, group_name, scheduler, tg_group_id):        
    return ScrapyCore()

@start_menu_router.message(StateFilter("*"), F.text == "Назад")
async def main_menu(message: types.Message, session: AsyncSession, scheduler = None):
    try:
        products = await scrapy_core.get_data_from_db(model=Products, session=session)
        posts = await scrapy_core.get_data_from_db(model=Posts, session=session)
        bd_count_text = f"В бд ВБ {hbold(len(products))} товаров"
        tgbd_count_text = f"В бд ТГ {hbold(len(posts))} постов"
        delay_count_text = (
            f"Постов в отложке {hbold(len(scheduler_app.get_delayed_posts(scheduler)))}"
        )
        await message.answer(
            text=f"{hbold('Главное меню')}\n{bd_count_text}\n{tgbd_count_text}\n{delay_count_text}\n{get_weather()}",
            reply_markup=get_keyboard(
                "Листать посты",
                "Отложка",
                "Парсер",
                "Очистка БД",
                "Категории",
                placeholder="Главное меню",
                sizes=(2, 2, 1),
            ),
            parse_mode="HTML",
        )
    except NameError:
        await start_point(message)


@start_menu_router.message(StateFilter("*"), F.text == "Одежда тпшкам")
@start_menu_router.message(StateFilter("*"), F.text == "Для дома")
@start_menu_router.message(StateFilter("*"), F.text == "Бижутерия")
async def state_router(message: types.Message, session: AsyncSession, group_name: str):
    if group_name:
        await main_menu(message, session)
    else:
        await message.answer("Не работает")


@start_menu_router.message(StateFilter("*"), F.text == "Категории")
@start_menu_router.message(CommandStart)
async def start_point(message: types.Message):
    await message.answer(
        text="Выберите категорию",
        reply_markup=get_keyboard(
            "Одежда тпшкам",
            "Для дома",
            "Бижутерия",
            "Косметика",
            placeholder="Категория",
            sizes=(2, 2),
        ),
    )
