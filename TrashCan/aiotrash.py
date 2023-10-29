async def sender(message: types.Message):
    try:
        post_text, pic_url, post_url = prepare_posts()
    except TypeError:
        await bot.send_message(message.chat.id, "Посты закончились")
        return
    except ValueError:
        post_text, pic_url, post_url = prepare_posts()

    pictures = [InputMediaPhoto(media=pic, parse_mode="HTML") for pic in pic_url]
    pictures[0].caption = post_text
    await bot.send_media_group(chat_id=message.chat.id, media=pictures)
    return post_url

if wbparse:
    await bot.send_message(message.chat.id, "Высылаю посты.", reply_markup=main_kb)
    await router(message=message, user_message="start")


async def router(message: types.Message, user_message=""):
    user_message: str = user_message.lower()
    if user_message == "запостить":
        to_post = await sender(message=message)
        post_exist = tg_sql.is_post_in_db(to_post)

        if post_exist:
            tg_sql.set_post_status(wb_id=to_post, status="Liked")
        elif post_exist == False:
            tg_sql.add_post(wb_id=to_post, status="Liked")
        return to_post

    elif user_message == "скип":
        to_post = await sender(message=message)

    elif user_message == "start":
        await sender(message=message)
if post_exist:
    tg_sql.set_post_status(wb_id=from_start_to_post, status="Liked")

elif post_exist is False:
    tg_sql.add_post(wb_id=from_start_to_post, status="Liked")

return from_start_to_post
