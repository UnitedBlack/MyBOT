from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.executor import start_polling

from aiogram_fsm import FSMContext, FSMMachine, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import sql
import tg_sql
import json
import ast

TOKEN = "6616429815:AAHlnRicZwp7C8P9JUxlN-pBC7JE16IwTxE"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(FSMMachine):
    wait_for_post_or_skip = State()

async def wbparse():
    all_products = sql.get_all_products()
    return all_products

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Вб")
    main_kb.add(types.KeyboardButton("/update"))
    await message.answer("Инициализируюсь", reply_markup=main_kb)
    await message.delete()
    await send_wbparse(message)

@dp.message(Command("update"))
async def send_wbparse(message: types.Message):
    wbparse_result = await wbparse()
    posts_list = []
    for item in wbparse_result:
        url = item.get("url")
        wb_id = item.get("wb_id")

        name = item.get("name")
        discount_price = item.get("discount_price")
        price = item.get("price")
        star_rating = item.get("star_rating")
        pic_url = item.get("pic_url")
        composition = item.get("composition")
        color = item.get("color")

        post = f"🎁 {hbold(name)}" if name else ""
        post += f"\n💵Цена: {hstrikethrough(price)}₽ {hbold(discount_price)}₽" if price and discount_price else ""
        post += f"\n🌟Рейтинг: {hbold(star_rating)}" if star_rating else ""
        post += f"\n🔬Состав: {hbold(composition)}" if composition else ""
        post += f"\n🌈Цвет: {hbold(color)}" if color else ""
        post += f"\n🔗Купить: {url}" if url else ""

        posts_list.append({"post_text": post, "post_pic": pic_url})

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("/showposts"))
    await message.answer("Закончил обновляться", reply_markup=kb)
    await show_posts(message)

@dp.message(Command("showposts"))
async def show_posts(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("Запостить"), types.KeyboardButton("Скип"))
    await message.answer("Высылаю посты", reply_markup=kb)
    await Form.wait_for_post_or_skip.set()
    
# @dp.message(state=Form.wait_for_post_or_skip)
# async def process_post_or_skip(message: types.Message, state: FSMContext):
#     if message.text.lower() in ["запостить", "скип"]:
#         print("da")
#     else:
#         await message.answer("Посты закончились")
#         kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         kb.add(types.KeyboardButton("/showposts"))
#         await message.answer("Выберите действие", reply_markup=kb)
#         await state.finish()
#     else:
#         await message.answer("Пожалуйста, введите 'Запостить' или 'Скип'")


if __name__ == "__main__":
    start_polling(dp)
                                
