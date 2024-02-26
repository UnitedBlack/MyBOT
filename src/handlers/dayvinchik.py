from aiogram import types, Router
from aiogram.filters import CommandStart

dayvinchik_router = Router()

@dayvinchik_router.message_handler(state=States.sender)
async def sender(message: types.Message):
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
    await States.wait_state.set()
    global pictures
    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pic_url]
    pictures[0].caption = post_text
    await bot.send_media_group(chat_id=admin_id, media=pictures)
    return


@dayvinchik_router.message_handler(
    regexp="^[Зз]апостить|[Сс]кип$",
    state=States.wait_state,
)
async def post_or_skip(message: types.Message):
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
