from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, Application, ContextTypes
import asyncio
import sql
import tg_sql


# STARTING, TYPING_REPLY, TYPING_CHOICE, WAITING = 
START, UPDATE_DB, SHOW_POSTS, WAITING, TYPING_CHOICE = range(5)

def wbparse():
    all_products = sql.get_all_products()
    return all_products

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # main_keyboard = ReplyKeyboardMarkup([[KeyboardButton('/update')]], resize_keyboard=True, input_field_placeholder='Вб')
    await update.message.reply_text('Инициализируюсь')
    return UPDATE_DB

async def update_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wbparse_result = wbparse()
    await update.message.reply_text(text='Закончил обновление. Высылаю посты.')
    return SHOW_POSTS


async def show_posts(update: Update, context: CallbackContext):
    print("Im here")
    wbparse_result = wbparse()
    for item in wbparse_result:
        url = item.get("url")
        wb_id = item.get("wb_id")
        tg_sql.create_or_connect_database()
        sql.create_or_connect_database()
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
        
        post = f"🎁 {name}" if name else ""
        post += f"\n💵Цена: <s>{price}₽</s> <b>{discount_price}</b>₽" if price and discount_price else ""
        post += f"\n🌟Рейтинг: <b>{star_rating}</b>" if star_rating else ""
        post += f"\n🔬Состав: <b>{composition}</b>" if composition else ""
        post += f"\n🌈Цвет: <b>{color}</b>" if color else ""
        post += f"\n🔗Купить: {url}" if url else ""
        media = [InputMediaPhoto(media_group) for media_group in pic_url]
        to_post_or_skip_kb = ReplyKeyboardMarkup([[KeyboardButton("Запостить")], [KeyboardButton("Скип")]], resize_keyboard=True)
            
        await update.message.reply_media_group(media=media, parse_mode='HTML', caption=post)
        await update.message.edit_reply_markup(to_post_or_skip_kb)
        wbparse_result.pop(0)
        await asyncio.sleep(1)
        
        tg_sql.add_post(wb_id)
        
        return WAITING


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message.text.lower())
    text = update.message.text
    if text.lower() == 'запостить':
        return SHOW_POSTS
    elif text.lower() == 'скип':
        return SHOW_POSTS
    else:
        await update.message.reply_text("Пожалуйста, введите 'Запостить' или 'Скип'.")
        return WAITING

    

def main() -> None:
    application = Application.builder().token("6616429815:AAHlnRicZwp7C8P9JUxlN-pBC7JE16IwTxE").build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('update', update_db)],
        states={
            # UPDATE_DB: [
            #     CommandHandler('update', update_db)
            # ],
            SHOW_POSTS: [
                CommandHandler('show', show_posts),
                MessageHandler(filters.Regex("^Запостить$"), show_posts)
            ],
            WAITING: [
                MessageHandler(filters.TEXT, text_message)
            ]
        },  
        fallbacks=[],
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()


# async def show_posts(update: Update, context: CallbackContext):
#     posts_list = await context.user_data.get("posts_list")
#     if not posts_list:
#         await update.message.reply_text("Посты закончились")
#         return WAITING

#     post = posts_list.pop(0)
#     pics = post['post_pic']
#     media = [InputMediaPhoto(url) for url in pics]
#     media[0].caption = post['post_text']

#     await update.message.reply_media_group(update.message.id, media=media)

#     return WAITING






# async def show_posts(update: Update, context: CallbackContext):
#     wbparse_result = wbparse()
#     for item in wbparse_result:
#         url = item.get("url")
#         wb_id = item.get("wb_id")
#         tg_sql.create_or_connect_database()
#         sql.create_or_connect_database()
#         is_in_db = tg_sql.is_post_in_db(wb_id)
#         post_status = tg_sql.get_post_status(wb_id)
#         if is_in_db and post_status == "Liked" or post_status == "Disliked": continue

#         name = item.get("name")
#         discount_price = item.get("discount_price")
#         price = item.get("price")
#         star_rating = item.get("star_rating")
#         pic_url = item.get("pic_url")
#         composition = item.get("composition")
#         color = item.get("color")

#         sql_string  = pic_url.strip('[]').strip()
#         pic_url = [url.strip() for url in sql_string.replace("'", "").split(',')]

#         post = f"🎁 {name}" if name else ""
#         post += f"\n💵Цена: <s>{price}₽</s> <b>{discount_price}₽</b>" if price and discount_price else ""
#         post += f"\n🌟Рейтинг: <b>{star_rating}</b>" if star_rating else ""
#         post += f"\n🔬Состав: <b>{composition}</b>" if composition else ""
#         post += f"\n🌈Цвет: <b>{color}</b>" if color else ""
#         post += f"\n🔗Купить: {url}" if url else ""
#         media = [InputMediaPhoto(media_group) for media_group in pic_url]

#         await update.message.reply_media_group(media=media, parse_mode='HTML', caption=post)

#         tg_sql.add_post(wb_id)

#         return WAITING