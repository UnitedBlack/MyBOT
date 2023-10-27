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


def main() -> None:
    application = (
        Application.builder()
        .token("6616429815:AAHlnRicZwp7C8P9JUxlN-pBC7JE16IwTxE")
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("show", show_posts))
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# сделать по-своему