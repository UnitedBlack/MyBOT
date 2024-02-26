from aiogram import types, Router
from aiogram.filters import CommandStart

delayed_menu_router = Router()


@delayed_menu_router.message_handler(
    regexp="^Удалить пост|Изменить время|Кастомный пост|Очистить всю отложку$",
    state=States.delayed_menu,
)
async def ask_delayed_id(message: types.Message):
    match message.text:
        case "Удалить пост":
            await States.delayed_delete.set()
            await bot.send_message(message.chat.id, text="Пришлите ID отложки")
        case "Изменить время":
            await States.delayed_change.set()
            await bot.send_message(
                message.chat.id,
                text="Пришлите ID отложки'",
            )
        case "Кастомный пост":
            await States.custom_post.set()
            await send_calendar_inline_kb()
        case "Очистить всю отложку":
            await bot.send_message(
                chat_id=admin_id,
                text="Вы уверены, что хотите удалить ВСЕ отложенные посты?",
                reply_markup=get_approve_kb(),
            )
            await States.clear_delayed.set()


@delayed_menu_router.message_handler(regexp="^Да$", state=States.clear_delayed)
async def clear_delayed_posts(message: types.Message):
    scheduler_app.remove_all_jobs(scheduler)
    await bot.send_message(admin_id, "Удалил все посты из отложки")
    await delayed_menu(message)


@delayed_menu_router.message_handler(state=States.delayed_change)
async def get_delayed_id(message: types.Message):
    global delayed_id
    await States.delayed_change_date.set()
    delayed_id = message.text
    year, month = datetime.now().year, datetime.now().month
    await bot.send_message(
        admin_id,
        f"📅Выберите день и время: ",
        reply_markup=create_calendar(
            year,
            month,
        ),
    )


@delayed_menu_router.message_handler(state=States.delayed_change_date)
async def change_post_delayed_time(message: types.Message):
    data = {
        "job_id": delayed_id,
        "custom_month": calendar_month,
        "custom_day": calendar_day,
        "custom_hour": calendar_hour,
        "custom_minute": calendar_minute,
    }
    scheduler_app.reschedule_post(data, scheduler)
    await message.reply("Изменил")
    await delayed_menu(message)


@delayed_menu_router.message_handler(state=States.delayed_delete)
async def delete_delayed_post(message: types.Message, state: FSMContext):
    delayed_id = message.text
    scheduler_app.delete_job(delayed_id, scheduler)
    await state.finish()
    await delayed_menu(message)
