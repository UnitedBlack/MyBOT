import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv

from handlers.start_menu import start_menu_router

# from handlers.main_menu import main_menu_router
# from handlers.callbacks import callback_handler_router
# from handlers.clear_database import clear_database_router
# from handlers.custom_post_menu import custom_post_menu_router
# from handlers.dayvinchik import dayvinchik_router
# from handlers.delayed_menu import delayed_menu_router
# from handlers.errors import error_handler_router

from middlewares.db import DatabaseSession

from database.engine import create_db, session_maker

load_dotenv(find_dotenv())

ALLOWED_UPDATES = []

bot = Bot(token=os.getenv("TOKEN"))
bot.admins_list = [333253716, 5049131938]

dp = Dispatcher()

dp.include_routers(
    # main_menu_router,
    # callback_handler_router,
    # clear_database_router,
    # custom_post_menu_router,
    # dayvinchik_router,
    # delayed_menu_router,
    start_menu_router,
    # error_handler_router,
)


async def on_startup(bot):
    await create_db()
    print("Ready")


async def on_shutdown(bot):
    print("Shut down")


async def main():
    dp.startup.register(on_startup)
    dp.startup.register(on_shutdown)
    dp.update.middleware(DatabaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # allowed_updates = ALLOWED_UPDATES


if __name__ == "__main__":
    asyncio.run(main())

# class States(StatesGroup):
#     delayed_menu = State()
#     delayed_delete = State()
#     delayed_change = State()
#     delayed_change_date = State()
#     start = State()
#     sender = State()
#     wait_state = State()
#     custom_post = State()
#     custom_post_link = State()
#     custom_post_menu = State()
#     edit_description = State()
#     edit_picture = State()

#     parser = State()
#     clear_delayed = State()
