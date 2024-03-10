from aiogram import types, Router, F
from aiogram.types import InputMediaPhoto
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.admin_filter import IsAdmin

from start_menu import StartMenuStates, main_menu
from database import service_db
import old.scheduler_app as scheduler_app

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
        if len(service_db.get_all_products()) < 1:
            await message.answer("БД с товарами пустая")
        elif len(service_db.get_all_products) == len(service_db.get_all_posts):
            await message.answer("Закончились товары")
        else:
            await message.answer("Посты закончились или какая-то ошибка")
        await state.set_state(StartMenuStates.start)
        await main_menu(message)
        return
    except ValueError as e:
        post_text, pic_url, post_url = scrapy.prepare_posts()
        print(e)
    await state.set_state(DayvicnikStates.wait)
    global pictures
    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pic_url]
    pictures[0].caption = post_text
    await message.answer_media_group(media=pictures)
    return


@dayvinchik_router.message(F.text == "Запостить", StatesGroup(DayvicnikStates.wait))
@dayvinchik_router.message(F.text == "Скип", StatesGroup(DayvicnikStates.wait))
async def post_or_skip(message: types.Message, state: FSMContext):
    try:
        user_message = message.text.lower()
    except AttributeError:
        user_message = "скип"
    await state.set_state(DayvicnikStates.sender)
    if user_message == "запостить":
        delay_data = {"post_text": post_text, "post_pic": pic_url, "chat_id": chat_id} # chat_id = group_id
        scheduler_app.schedule_post(delay_data, scheduler)
        service_db.update_post_status(id=post_url, status="Liked")
        # append_data_to_db
        await sender(message=message)
    elif user_message == "скип":
        # не обязательно update_post_status, мб add post а или хз
        service_db.update_post_status(id=post_url, status="Disliked")
        # scrapy.append_data_to_db(post_url, "Disliked")
        await sender(message=message)
