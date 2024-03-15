from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.reply import get_keyboard
from database import service_db
from filters.admin_filter import IsAdmin

from database.models import Products, Posts

clear_database_router = Router()
clear_database_router.message.filter(IsAdmin())


class ClearDatabase(StatesGroup):
    clear_database = State()


@clear_database_router.message(StateFilter("*"), F.text == "Очистка БД")
async def clear_db(message: types.Message, state: FSMContext):
    await message.answer(
        text="Какую бд хотите очистить?",
        reply_markup=get_keyboard(
            "Очистить ВБ БД", "Очистить ТГ БД", "Назад", sizes=(3)
        ),
    )
    await state.set_state(ClearDatabase.clear_database)


@clear_database_router.message(
    StateFilter(ClearDatabase.clear_database), F.text == "Очистить ВБ БД"
)
async def clear_wb(message: types.Message, state: FSMContext):
    service_db.delete_all_records(table=Posts, group_name=...)
    # products_sql.delete_all_records(wb_table_name)
    await message.reply("Очистил")
    # get_scrapy()


@clear_database_router.message(
    StateFilter(ClearDatabase.clear_database),
    F.text == "Очистить ТГ БД",
)
async def clear_tg(message: types.Message, state: FSMContext):
    service_db.delete_all_records(table=Products, group_name=...)
    # posts_sql.delete_all_records(tg_table_name)
    await message.reply("Очистил")
    # get_scrapy()
