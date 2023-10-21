import json
import time
import asyncio
import aiofiles
import logging
import sys
import os
import shutil
import re
import main
import sql

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from aiogram.utils.markdown import hbold, hstrikethrough, hunderline
from aiogram.types import InputMediaPhoto
from aiogram.methods import SendMediaGroup
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "6616429815:AAHlnRicZwp7C8P9JUxlN-pBC7JE16IwTxE"
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
me = ["333253716", "1074422484"]


def add_callback_data_to_db():
    return "Added"


def wbparse():
    all_products = sql.get_all_products()
    return all_products


@dp.message(Command("update"))
async def send_wbparse(message: types.Message):
    wbparse_result = wbparse()
    # message_id = message.message_id  # Получаем ID сообщения
    # builder.button(text="Лайк", callback_data=f"like_{message_id}")  # Добавляем ID сообщения в callback_data
    # builder.button(text="Дизлайк", callback_data=f"likedis_{message_id}")
    for item in wbparse_result:
        builder = InlineKeyboardBuilder()   
        name = item.get("name")
        discount_price = item.get("discount_price")
        price = item.get("price")
        star_rating = item.get("star_rating")
        url = item.get("url")
        pic_url = item.get("pic_url")
        composition = item.get("composition")
        color = item.get("color")
        
        post = f"🎁 {hbold(name)}" if name else ""
        post += f"\n💵Цена: {hstrikethrough(price)}₽ {hbold(discount_price)}₽" if price and discount_price else ""
        post += f"\n🌟Рейтинг: {hbold(star_rating)}" if star_rating else ""
        post += f"\n🔬Состав: {hbold(composition)}" if composition else ""
        post += f"\n🌈Цвет: {hbold(color)}" if color else ""
        post += f"\n🔗Купить: {url}" if url else ""

        time.sleep(0.3)
        sent_message = await bot.send_message(message.chat.id, post)
        message_id = sent_message.message_id
        builder.button(text="Лайк", callback_data=f"post_{message_id}")  
        builder.button(text="Дизлайк", callback_data=f"post_{message_id}")
        # Обновляем клавиатуру сообщения
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id, reply_markup=builder.as_markup())

    
@dp.callback_query(lambda c: c.data.startswith('post'))
async def process_callback_post(callback_query: types.CallbackQuery):
    message_id = callback_query.data.split("_")[1]  # Извлекаем ID сообщения из callback_data
    button_type = callback_query.data.split("_")[0]  # Извлекаем тип кнопки из callback_data
    print(button_type)
    await bot.answer_callback_query(callback_query.id)
    if button_type == 'like':
        a = add_callback_data_to_db()
        print(a)
    await bot.send_message(callback_query.from_user.id, f'ID сообщения: {message_id}')
    # asd = await bot.copy_message(from_chat_id=callback_query.from_user.id, message_id=message_id)
    
async def main():
    await dp.start_polling(bot)
    
    
if __name__ == '__main__':
    asyncio.run(main())
    
    
# @dp.message(Command("update"))
# async def send_wbparse(message: types.Message):
#     builder = InlineKeyboardBuilder()   
#     builder.button(text="Запостить", callback_data="post")
#     wbparse_result = wbparse()
#     await bot.send_message(message.chat.id, wbparse_result, reply_markup=builder.as_markup())


# @dp.callback_query(lambda c: c.data == 'post')
# async def process_callback_post(callback_query: types.CallbackQuery):
#     # Здесь может быть ваш код для обработки нажатия на кнопку "Запостить"
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, 'Сообщение запощено!')

# @dp.callback_query(lambda c: c.data.startswith('post'))
# async def process_callback_post(callback_query: types.CallbackQuery):
#     message_id = callback_query.data.split("_")[1]  # Извлекаем ID сообщения из callback_data
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, f'Сообщение запощено! ID сообщения: {message_id}')
# await bot.send_message(message.chat.id, post, reply_markup=builder.as_markup())