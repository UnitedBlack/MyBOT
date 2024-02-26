from preknown_errors import *
from aiogram import types, Router

error_handler_router = Router()

@error_handler_router.error()
async def error_handler(update: types.Update, exception: Exception):
    await States.start.set()
    if str(exception) == scheduler_not_defined:
        await bot.send_message(admin_id, text="Забыл выбрать категорию")
        await start_point(update.message)
        return
    elif str(exception) in [tg_random_error, failed_to_send_message]:
        await bot.send_message(admin_id, text="Телеграм поносит, автоскипаю")
        await States.wait_state.set()
        await post_or_skip(update)
        return
    elif str(exception) in [aiogram_wrong_string_length, aiogram_badrequest]:
        await bot.send_message(admin_id, text="Аиограм поносит, нажмите кнопку скип")
        await States.wait_state.set()
        return
    elif str(exception) == playwright_random_error:
        return
    elif str(exception) == "NoneType' object has no attribute 'get":
        return
    else:
        await bot.send_message(admin_id, text=f"Не понятная мне ошибка\n{exception}")
        return
