import telebot
import sql
import tg_sql
import time
from telebot import types


TOKEN = "6616429815:AAHlnRicZwp7C8P9JUxlN-pBC7JE16IwTxE"
bot = telebot.TeleBot(TOKEN)

list_of_posts = []

def wbparse():
    sql.create_or_connect_database()
    all_products = sql.get_all_products()
    return all_products


@bot.message_handler(commands=['start'])
def send_welcome(message):
    main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Вб")
    main_kb.row(types.KeyboardButton("/update"))
    bot.send_message(message.chat.id, "Инициализируюсь", reply_markup=main_kb)
    bot.delete_message(message.chat.id, message.message_id)
    send_wbparse(message)


@bot.message_handler(commands=['update'])
def send_wbparse(message):
    wbparse_result = wbparse()
    for item in wbparse_result:
        url = item.get("url")
        wb_id = item.get("wb_id")

        tg_sql.create_or_connect_database()
        is_in_db = tg_sql.is_post_in_db(wb_id)
        post_status = tg_sql.get_post_status(wb_id)
        if is_in_db and post_status == "Liked" or post_status == "Disliked": continue
        # все равно добавляет дубликаты в бд

        name = item.get("name")
        discount_price = item.get("discount_price")
        price = item.get("price")
        star_rating = item.get("star_rating")
        pic_url = item.get("pic_url")
        composition = item.get("composition")
        color = item.get("color")

        sql_string  = pic_url.strip('[]').strip()
        pic_url = [url.strip() for url in sql_string.replace("'", "").split(',')]

        post = f"🎁 <b>{name}</b>" if name else ""
        post += f"\n💵Цена: <s>{price}</s>₽ <b>{discount_price}</b>₽" if price and discount_price else ""
        post += f"\n🌟Рейтинг: <b>{star_rating}</b>" if star_rating else ""
        post += f"\n🔬Состав: <b>{composition}</b>" if composition else ""
        post += f"\n🌈Цвет: <b>{color}</b>" if color else ""
        post += f"\n🔗Купить: {url}" if url else ""

        posts = {"post_text": post,"post_pic": pic_url}

        list_of_posts.append(posts)


    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(types.KeyboardButton("/showposts"))
    bot.send_message(message.chat.id, "Закончил обновляться", reply_markup=kb)
    show_posts(message)


@bot.message_handler(commands=['showposts'])
def show_posts(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(types.KeyboardButton("Запостить"), types.KeyboardButton("Скип"))
    bot.send_message(message.chat.id, "Высылаю посты", reply_markup=kb)
    handle_text(message)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if list_of_posts:
        post = list_of_posts.pop(0)
        # bot.send_message(message.chat.id, post["post_text"], parse_mode='HTML')
        # bot.send_photo()e

        media = [types.InputMediaPhoto(url, parse_mode="HTML") for url in post['post_pic']]
        media[0].caption = post['post_text']
        bot.send_media_group(message.chat.id, media)
        bot.send_message(message.chat.id, post['post_text'], parse_mode='HTML')
        bot.register_next_step_handler(message, handle_text)
    else:
        bot.send_message(message.chat.id, "Посты закончились")
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row(types.KeyboardButton("/showposts"))
        bot.send_message(message.chat.id, "Выберите действие", reply_markup=kb)


bot.infinity_polling()


# @bot.message_handler(commands=['clear'])
# def clear_database(message):
#     # tg_sql.clear_sql()
#     exit()

        # bot.send_message(chat_id, post, parse_mode='HTML')
        # while message.text != "Запостить" or message.text != "Скип":
        #     time.sleep(0.5)


# @bot.message_handler(content_types=['text'])
# def handle_text(message):
#     for post in list_of_posts:
#         bot.send_message(message.chat.id, post["post_text"], parse_mode='HTML')
#         bot.register_next_step_handler(message, process_step)

# def process_step(message):
#     if message.text == 'Запостить':
#         print("Pressed post")
#         # Здесь код для обработки действия "Запостить"
#     elif message.text == 'Скип':
#         print("pressed skip")
#         # Здесь код для обработки действия "Скип"

# import logging
# from aiogram import Bot, Dispatcher, types
# from aiogram.utils import executor
# from aiogram.utils.markdown import hbold, hstrikethrough
# from aiogram import types
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Command
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.contrib.fsm_storage.memory import MemoryStorage

# import sql
# import tg_sql
# import json
# import ast

# storage = MemoryStorage()
# TOKEN = "6616429815:AAHlnRicZwp7C8P9JUxlN-pBC7JE16IwTxE"
# bot = Bot(token=TOKEN)
# dp = Dispatcher(bot, storage=storage)

# list_of_posts = []


# class Form(StatesGroup):
#     wait_for_post_or_skip = State()


# async def wbparse():
#     all_products = sql.get_all_products()
#     return all_products


# @dp.message_handler(commands=["start"])
# async def send_welcome(message: types.Message):
#     main_kb = types.ReplyKeyboardMarkup(
#         resize_keyboard=True, input_field_placeholder="Вб"
#     )
#     main_kb.add(types.KeyboardButton("/update"))
#     await bot.send_message(message.chat.id, "Инициализируюсь", reply_markup=main_kb)
#     await bot.delete_message(message.chat.id, message.message_id)
#     await send_wbparse(message)


# @dp.message_handler(commands=["update"])
# async def send_wbparse(message: types.Message):
#     wbparse_result = await wbparse()
#     for item in wbparse_result:
#         url = item.get("url")
#         wb_id = item.get("wb_id")

#         name = item.get("name")
#         discount_price = item.get("discount_price")
#         price = item.get("price")
#         star_rating = item.get("star_rating")
#         pic_url = item.get("pic_url")
#         composition = item.get("composition")
#         color = item.get("color")

#         post = f"🎁 {hbold(name)}" if name else ""
#         post += (
#             f"\n💵Цена: {hstrikethrough(price)}₽ {hbold(discount_price)}₽"
#             if price and discount_price
#             else ""
#         )
#         post += f"\n🌟Рейтинг: {hbold(star_rating)}" if star_rating else ""
#         post += f"\n🔬Состав: {hbold(composition)}" if composition else ""
#         post += f"\n🌈Цвет: {hbold(color)}" if color else ""
#         post += f"\n🔗Купить: {url}" if url else ""

#         posts = {"post_text": post, "post_pic": pic_url}

#         list_of_posts.append(posts)

#     kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     kb.add(types.KeyboardButton("/showposts"))
#     await bot.send_message(message.chat.id, "Закончил обновляться", reply_markup=kb)
#     await show_posts(message)


# @dp.message_handler(commands=["showposts"])
# async def show_posts(message: types.Message):
#     kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     kb.add(types.KeyboardButton("Запостить"), types.KeyboardButton("Скип"))
#     await bot.send_message(message.chat.id, "Высылаю посты", reply_markup=kb)
#     await Form.wait_for_post_or_skip.set()


# @dp.message_handler(state=Form.wait_for_post_or_skip)
# async def process_post_or_skip(message: types.Message, state: FSMContext):
#     if message.text.lower() in ["запостить", "скип"]:
#         if list_of_posts:
#             post = list_of_posts.pop(0)
#             pics = ast.literal_eval(post["post_pic"])
#             media = [
#                 types.InputMediaPhoto(url, parse_mode="HTML", caption=post["post_text"])
#                 for url in pics
#             ]
#             await bot.send_media_group(message.chat.id, media)
#             await Form.wait_for_post_or_skip.set()
#         else:
#             await bot.send_message(message.chat.id, "Посты закончились")
#             kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
#             kb.add(types.KeyboardButton("/showposts"))
#             await bot.send_message(
#                 message.chat.id, "Выберите действие", reply_markup=kb
#             )
#             await state.finish()
#     else:
#         await bot.send_message(
#             message.chat.id, "Пожалуйста, введите 'Запостить' или 'Скип'"
#         )


# if __name__ == "__main__":
#     from aiogram import executor

#     executor.start_polling(dp, skip_updates=True)
