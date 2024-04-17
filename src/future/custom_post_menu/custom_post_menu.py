from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from filters.admin_filter import IsAdmin

custom_post_menu_router = Router()
custom_post_menu_router.message.filter(IsAdmin())

class CustomPostMenuState(StatesGroup):
    custom_post = State()

# @custom_post_menu_router.message(regexp="^Запостить$", state=States.custom_post_menu)
# async def delay_custom_post(message: types.Message):
#     custom_time = (
#         calendar_hour,
#         calendar_minute,
#         calendar_day,
#         calendar_month,
#         calendar_year,
#     )
#     delay_data = {
#         "post_text": post_text,
#         "post_pic": pictures,
#     }  # user_pics if user_pics else pics
#     scheduler_app.schedule_post(delay_data, scheduler, ad=True, custom_time=custom_time)
#     await bot.send_message(
#         admin_id,
#         text=f"Добавил в отложку, время {calendar_hour}:{calendar_minute} {calendar_day}-{calendar_month}",
#     )
#     await delayed_menu(message)


# @custom_post_menu_router.message(state=States.edit_description)
# async def edit_description(message: types.Message):
#     await States.custom_post_menu.set()
#     global post_text
#     user_message = message.text
#     post_text = user_message
#     pictures[0].caption = user_message
#     await bot.send_message(admin_id, text=f"Так будет выглядеть ваш пост:")
#     await bot.send_media_group(chat_id=admin_id, media=pictures)


# @custom_post_menu_router.message(regexp="^Редактировать описание$", state=States.custom_post_menu)
# async def ask_edit_description(message: types.Message):
#     await bot.send_message(
#         admin_id,
#         text=f"{post_text}\n\nВот текст поста, пришлите текст для редактирования",
#         parse_mode="HTML",
#     )
#     await States.edit_description.set()


# @custom_post_menu_router.message(regexp="^Выйти без сохранения$", state="*")
# async def exit_without_saving(message: types.Message):
#     await delayed_menu(message)


# @custom_post_menu_router.message(content_types=["photo"], state=States.edit_picture)
# async def edit_picture(message: types.Message):
#     await bot.send_message(
#         admin_id, "Сохранил. Ещё одну?", reply_markup=get_photo_editor_kb()
#     )  # Клавиатуру типа "ВСЕ ХВАТИТ"
#     user_pic = message.photo[-1].file_id  # Get the largest size of the photo
#     user_pics.append(user_pic)  # Store the photo


# @custom_post_menu_router.message(state=States.edit_picture)
# async def process_pictures(message: types.Message):
#     if message.text == "Закончить":
#         global pictures
#         pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in user_pics]
#         pictures[0].caption = post_text
#         await bot.send_media_group(chat_id=admin_id, media=pictures)
#         user_pics.clear()  # Clear the list for the next set of photos
#         await bot.send_message(
#             admin_id, "Вот ваш пост", reply_markup=get_custom_post_kb()
#         )
#         await States.custom_post_menu.set()
#     elif message.text == "Добавить фото":
#         await bot.send_message(admin_id, "Присылайте по ОДНОЙ фотографии")
#     elif message.text == "Удалить фото":
#         ...


# @custom_post_menu_router.message(regexp="^Редактировать фото$", state=States.custom_post_menu)
# async def ask_edit_picture(message: types.Message):
#     await States.edit_picture.set()
#     await bot.send_message(
#         admin_id, "Вы в редакторе фото", reply_markup=get_edit_photo_kb()
#     )
#     pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pics]
#     pictures[0].caption = "Это фотографии поста, как хотите изменить?"
#     await bot.send_media_group(chat_id=admin_id, media=pictures)


# @custom_post_menu_router.message(state=States.custom_post_link)
# async def create_custom_post(message: types.Message):
#     global post_text, pics, custom_data
#     user_link = [message.text]
#     await bot.send_message(
#         admin_id, text="Вызываю парсер", reply_markup=get_custom_post_kb()
#     )
#     custom_data = await custom_scraper.main(user_link[0])
#     post_text = scrapy.format_post(custom_data)
#     pics = literal_eval(custom_data["pic_url"])
#     pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pics]
#     pictures[0].caption = post_text
#     await bot.send_media_group(chat_id=admin_id, media=pictures)
#     await States.custom_post_menu.set()
