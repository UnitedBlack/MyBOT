import asyncio
import TrashCan.main_test as main_test
import sql
import tg_sql

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from aiogram.utils.markdown import hbold, hstrikethrough, hunderline
from aiogram.types import InputMediaPhoto, InputMedia
from aiogram.methods import SendMediaGroup
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

TOKEN = "6616429815:AAHlnRicZwp7C8P9JUxlN-pBC7JE16IwTxE"
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

    
def wbparse():
    all_products = sql.get_all_products()
    return all_products

@dp.message(CommandStart)
async def start(message: Message):
    main_kb = ReplyKeyboardMarkup(
        keyboard=[
            KeyboardButton(text="Запостить"),
            KeyboardButton(text="Скип")
        ],
        resize_keyboard=True,
        input_field_placeholder="Вб залупа")
    await message.answer(text="ВБ", reply_markup=main_kb)
    

@dp.message(Command("clear"))
async def clear_database(message: types.Message):
    tg_sql.clear_sql()
    exit()

@dp.message(Command("update"))
async def send_wbparse(message: types.Message):
    wbparse_result = wbparse()
    for item in wbparse_result:
        url = item.get("url")
        wb_id = item.get("wb_id")
        
        is_in_db = tg_sql.is_post_in_db(wb_id)
        post_status = tg_sql.get_post_status(wb_id)
        if is_in_db and post_status == "Liked" or post_status == "Disliked": continue
        # все равно мразь добавляет дубликаты в бд
        
        name = item.get("name")
        discount_price = item.get("discount_price")
        price = item.get("price")
        star_rating = item.get("star_rating")
        pic_url = item.get("pic_url")
        composition = item.get("composition")
        color = item.get("color")
        
        sql_string  = pic_url.strip('[]').strip()
        pic_url = [url.strip() for url in sql_string.replace("'", "").split(',')]
        
        post = f"🎁 {hbold(name)}" if name else ""
        post += f"\n💵Цена: {hstrikethrough(price)}₽ {hbold(discount_price)}₽" if price and discount_price else ""
        post += f"\n🌟Рейтинг: {hbold(star_rating)}" if star_rating else ""
        post += f"\n🔬Состав: {hbold(composition)}" if composition else ""
        post += f"\n🌈Цвет: {hbold(color)}" if color else ""
        post += f"\n🔗Купить: {url}" if url else ""

        media_group = MediaGroupBuilder(caption=post)
        for pic in pic_url:
            media_group.add(type="photo", media=pic)
            
        builded_media = media_group.build()
        
        
        tg_sql.add_post(wb_id)
        
    
@dp.callback_query(lambda c: c.data.startswith('action'))
async def process_callback_post(callback_query: types.CallbackQuery):
    message_id = callback_query.data  # Извлекаем ID сообщения из callback_data
    button_type = callback_query.data.split("_")[1]
    wb_id = callback_query.data.split("_")[2]

    await bot.answer_callback_query(callback_query.id)
    
    if button_type == 'like':
        tg_sql.set_post_status(wb_id=wb_id, status="Liked")
    elif button_type == 'dislike':
        tg_sql.set_post_status(wb_id=wb_id, status="Disliked")
     
    await bot.send_message(callback_query.from_user.id, f'ID сообщения: {message_id}')

    
async def main_test():
    await dp.start_polling(bot)
    
    
if __name__ == '__main__':
    asyncio.run(main_test())
    
    
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

   # url_text = callback_query.data
    # print(f"Была нажата кнопка 'лайк' под сообщением с id={callback_query.message.message_id} и текстом: '{url_text}'")
            # await bot.edit_message_media(chat_id=message.chat.id, message_id=message_id, reply_markup=builder.as_markup())
        # await bot.edit_message_media(chat_id=message.chat.id, message_id=message_id, reply_markup=builder.as_markup(), media="")
        # await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id, reply_markup=builder.as_markup(), )
                # builder = InlineKeyboardBuilder()
        # builder.button(text="Лайк", callback_data=f"action_like_{wb_id}")  
        # builder.button(text="Дизлайк", callback_data=f"action_dislike_{wb_id}")