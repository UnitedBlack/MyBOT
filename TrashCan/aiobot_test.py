import parser_app
import scheduler_app
import logging
from sql_data import posts_sql, products_sql
from TrashCan.main_test import main
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
    failed_to_send_message,
    scheduler_not_defined,
)


class States(StatesGroup):
    delayed_menu = State()


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler()
async def operator(message: types.Message, state: FSMContext):
    print(message.text)


@dp.message_handler(commands=["start"])
async def start_point(message: types.Message):
    await States.delayed_menu.set()
    await bot.send_message(
        chat_id=admin_id,
        text="Пришлите текст кастомного поста",
    )


executor.start_polling(dp, skip_updates=True)
