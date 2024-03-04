from aiogram import types, Router
from aiogram.filters import CommandStart

from filters.admin_filter import IsAdmin

callback_handler_router = Router()
callback_handler_router.message.filter(IsAdmin())

async def send_calendar_inline_kb():
    year, month = datetime.now().year, datetime.now().month
    await bot.send_message(
        admin_id,
        f"📅Выберите день и время: ",
        reply_markup=create_calendar(
            year,
            month,
        ),
    )


@callback_handler_router.callback_query(
    lambda c: c.data and c.data.startswith("prev-month"),
    state="*",
)
async def process_callback_prev_month(callback_query: types.CallbackQuery):
    _, month, _, year = callback_query.data.split("-")[1:]
    month, year = int(month), int(year)
    month -= 1
    if month < 1:
        month = 12
        year -= 1
    markup = create_calendar(year, month)
    await bot.edit_message_text(
        "📅Выберите день и время: ",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=markup,
    )
    await callback_query.answer()


@callback_handler_router.callback_query(
    lambda c: c.data and c.data.startswith("next-month"),
    state="*",
)
async def process_callback_next_month(callback_query: types.CallbackQuery):
    _, month, _, year = callback_query.data.split("-")[1:]
    month, year = int(month), int(year)
    month += 1
    if month > 12:
        month = 1
        year += 1
    markup = create_calendar(year, month)
    await bot.edit_message_text(
        "📅Выберите день и время: ",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=markup,
    )
    await callback_query.answer()


@callback_handler_router.callback_query(
    lambda c: c.data and c.data.startswith("calendar"), state="*"
)
async def process_callback_calendar(callback_query: types.CallbackQuery):
    global calendar_day, calendar_month, calendar_year
    _, calendar_day, calendar_month, calendar_year = callback_query.data.split("-")
    await bot.edit_message_reply_markup(
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=create_time_kb(),
    )


@callback_handler_router.callback_query(
    lambda c: c.data and c.data.startswith("time"), state=States.delayed_change_date
)
async def process_callback_calendar_time(callback_query: types.CallbackQuery):
    global calendar_hour, calendar_minute
    _, calendar_hour, calendar_minute = callback_query.data.split("-")
    await change_post_delayed_time(message=callback_query.message)


@callback_handler_router.callback_query(
    lambda c: c.data and c.data.startswith("time"), state=States.custom_post
)
async def process_callback_calendar_time(callback_query: types.CallbackQuery):
    global calendar_hour, calendar_minute
    _, calendar_hour, calendar_minute = callback_query.data.split("-")
    await States.custom_post_link.set()
    await bot.delete_message(
        callback_query.from_user.id,
        callback_query.message.message_id,
    )
    await bot.send_message(
        admin_id,
        text=f"Выбранное время: {calendar_hour}:{calendar_minute} {calendar_day}-{calendar_month}\nПришлите ссылку на товар",
        reply_markup=get_time_back_kb(),
    )


@callback_handler_router.callback_query(
    lambda c: c.data and c.data.startswith("back-time"),
    state="*",
)
async def send_calendar_keyboard(callback_query: types.CallbackQuery):
    year, month = datetime.now().year, datetime.now().month
    await bot.edit_message_reply_markup(
        callback_query.from_user.id,
        callback_query.message.message_id,
        f"📅Выберите день и время: ",
        reply_markup=create_calendar(
            year,
            month,
        ),
    )


@callback_handler_router.callback_query(
    lambda c: c.data and c.data.startswith("change-time"),
    state="*",
)
async def change_inline_time(callback_query: types.CallbackQuery):
    await States.custom_post.set()
    year, month = datetime.now().year, datetime.now().month
    await bot.edit_message_reply_markup(
        callback_query.from_user.id,
        callback_query.message.message_id,
        f"📅Выберите день и время: ",
        reply_markup=create_calendar(
            year,
            month,
        ),
    )
    # await send_calendar_inline_kb()
