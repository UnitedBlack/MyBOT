from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputMediaPhoto,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext,
    Application,
    ContextTypes,
    CallbackQueryHandler,
)
import asyncio
import sql
import tg_sql
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

OPERATE_TEXT, SHOW_POST, BRUH = range(3)


def wbparse() -> dict:
    all_products = sql.get_all_products()
    return all_products


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    main_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="/update", callback_data="0")]],
    )
    await update.message.reply_text(text="Инициализируюсь", reply_markup=main_keyboard)
    # return UPDATE_DB


async def update_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global wbparse_result
    wbparse_result = wbparse()
    show_posts_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="/show", callback_data='0')]],
    )
    await update.message.reply_text(
        text="Закончил обновление. Высылаю посты.", reply_markup=show_posts_keyboard
    )
    return BRUH


async def show_posts(update: Update, context: CallbackContext):
    print("Im here")
    try:
        wbparse_result.pop(0)
    except IndexError:
        return False
    for item in wbparse_result:
        url = item.get("url")
        wb_id = item.get("wb_id")
        tg_sql.create_or_connect_database()
        sql.create_or_connect_database()
        is_in_db = tg_sql.is_post_in_db(wb_id)
        post_status = tg_sql.get_post_status(wb_id)
        if is_in_db and post_status == "Liked" or post_status == "Disliked":
            continue
        # все равно мразь добавляет дубликаты в бд

        name = item.get("name")
        discount_price = item.get("discount_price")
        price = item.get("price")
        star_rating = item.get("star_rating")
        pic_url = item.get("pic_url")
        composition = item.get("composition")
        color = item.get("color")

        sql_string = pic_url.strip("[]").strip()
        pic_url = [url.strip() for url in sql_string.replace("'", "").split(",")]

        post = f"🎁 {name}" if name else ""
        post += (
            f"\n💵Цена: <s>{price}₽</s> <b>{discount_price}</b>₽"
            if price and discount_price
            else ""
        )
        post += f"\n🌟Рейтинг: <b>{star_rating}</b>" if star_rating else ""
        post += f"\n🔬Состав: <b>{composition}</b>" if composition else ""
        post += f"\n🌈Цвет: <b>{color}</b>" if color else ""
        post += f"\n🔗Купить: {url}" if url else ""
        media = [InputMediaPhoto(media_group) for media_group in pic_url]

        to_post_or_skip_kb = ReplyKeyboardMarkup(
            [[KeyboardButton("Запостить")], [KeyboardButton("Скип")]],
            resize_keyboard=True,
        )

        await update.message.reply_media_group(
            media=media, parse_mode="HTML", caption=post
        )

        tg_sql.add_post(wb_id)
        print("returning")
        return BRUH


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("here")
    text: str = update.message.text.lower()
    if text == "запостить":
        return await show_posts(update, context)
    elif text == "скип":
        return await show_posts(update, context)
    else:
        await update.message.reply_text("Пожалуйста, введите 'Запостить' или 'Скип'.")


def main() -> None:
    application = (
        Application.builder()
        .token("6616429815:AAHlnRicZwp7C8P9JUxlN-pBC7JE16IwTxE")
        .build()
    )
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("update", update_db)],
        states={
            BRUH: [CallbackQueryHandler(show_posts)],
            OPERATE_TEXT: [
                MessageHandler(
                    filters.Regex("^[Зз]апостить|[Сс]кип$"),
                    text_message,
                ),
            ],
            SHOW_POST: [CallbackQueryHandler(show_posts)],
        },
        fallbacks=[],
    )
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("show", show_posts))
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
