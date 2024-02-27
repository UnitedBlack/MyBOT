from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

clear_database_router = Router()


class ClearDatabase(StatesGroup):
    clear_database = State()


@clear_database_router.message(StateFilter("*"), F.text == "Очистка БД")
async def clear_db(message: types.Message, state: FSMContext):
    await bot.send_message(
        admin_id, text="Какую бд хотите очистить?", reply_markup=get_clear_db_kb()
    )
    await state.set_state(ClearDatabase.clear_database)


@clear_database_router.message(
    StateFilter(ClearDatabase.clear_database), F.text == "Очистить ВБ БД"
)
async def clear_wb(message: types.Message, state: FSMContext):
    products_sql.delete_all_records(wb_table_name)
    await message.reply("Очистил")
    get_scrapy()


@clear_database_router.message(
    StateFilter(ClearDatabase.clear_database),
    F.text == "Очистить ТГ БД",
)
async def clear_tg(message: types.Message, state: FSMContext):
    posts_sql.delete_all_records(tg_table_name)
    await message.reply("Очистил")
    get_scrapy()
