from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.admin_filter import IsAdmin
import scheduler_app

dayvinchik_router = Router()
dayvinchik_router.message.filter(IsAdmin())

class DayvicnikStates(StatesGroup):
    sender = State()
    wait = State()


@dayvinchik_router.message(StateFilter(DayvicnikStates.sender))
async def sender(message: types.Message, state: FSMContext):
    global post_url, pic_url, post_text
    try:
        post_text, pic_url, post_url = scrapy.prepare_posts()
    except TypeError as e:
        if scrapy.count_of_products_in_db() < 1:
            await bot.send_message(admin_id, "БД с товарами пустая")
        elif scrapy.count_of_products_in_db == scrapy.count_of_products_in_tgdb:
            await bot.send_message(admin_id, "Закончились товары")
        else:
            await bot.send_message(admin_id, "Посты закончились или какая-то ошибка")

        await States.start.set()
        await main_menu(message)
        return
    except ValueError as e:
        post_text, pic_url, post_url = scrapy.prepare_posts()
        print(e)
    await state.set_state(DayvicnikStates.wait)
    global pictures
    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pic_url]
    pictures[0].caption = post_text
    await bot.send_media_group(chat_id=admin_id, media=pictures)
    return


@dayvinchik_router.message(F.text == "Запостить", StatesGroup(DayvicnikStates.wait))
@dayvinchik_router.message(F.text == "Скип", StatesGroup(DayvicnikStates.wait))
async def post_or_skip(message: types.Message, state: FSMContext):
    try:
        user_message = message.text.lower()
    except AttributeError:
        user_message = "скип"
    await States.sender.set()
    if user_message == "запостить":
        delay_data = {"post_text": post_text, "post_pic": pic_url, "chat_id": chat_id}
        scheduler_app.schedule_post(delay_data, scheduler)
        scrapy.append_data_to_db(post_url, "Liked")
        await sender(message=message)
    elif user_message == "скип":
        scrapy.append_data_to_db(post_url, "Disliked")
        await sender(message=message)
