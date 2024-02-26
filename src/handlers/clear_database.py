from aiogram import types, Router
from aiogram.filters import CommandStart

clear_database_router = Router()


@clear_database_router.message_handler(regexp="^Очистить ТГ БД$", state=States.clear_database)
async def clear_tg(message: types.Message):
    posts_sql.delete_all_records(tg_table_name)
    await message.reply("Очистил")
    get_scrapy()


@clear_database_router.message_handler(regexp="^Очистить ВБ БД$", state=States.clear_database)
async def clear_wb(message: types.Message):
    products_sql.delete_all_records(wb_table_name)
    await message.reply("Очистил")
    get_scrapy()


@clear_database_router.message_handler(regexp="^Очистка БД$", state="*")
async def clear_db(message: types.Message):
    await bot.send_message(
        admin_id, text="Какую бд хотите очистить?", reply_markup=get_clear_db_kb()
    )
    await States.clear_database.set()
