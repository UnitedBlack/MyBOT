from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from future.custom_post_menu.custom_post_menu import CustomPostMenuState
from keyboards.reply import get_keyboard
from filters.admin_filter import IsAdmin
# from handlers.main_menu import delayed_menu, scheduler

import scheduler_app

delayed_menu_router = Router()
delayed_menu_router.message.filter(IsAdmin())


class DelayedMenuStates(StatesGroup):
    delayed_menu = State()
    delayed_delete = State()
    delayed_change = State()
    delayed_clear = State()
    delayed_change_date = State()


# @delayed_menu_router.message(
#     F.regexp == "^Удалить пост|Изменить время|Кастомный пост|Очистить всю отложку$",
#     StateFilter(DelayedMenuStates.delayed_menu),
# )
# async def ask_delayed_id(message: types.Message, state: FSMContext):
#     if message.text == "Удалить пост":
#         await state.set_state(DelayedMenuStates.delayed_delete)
#         await message.answer(message.chat.id, text="Пришлите ID отложки")
#     elif message.text == "Изменить время":
#         await state.set_state(DelayedMenuStates.delayed_change)
#         await message.answer(text="Пришлите ID отложки")
#     elif message.text == "Кастомный пост":
#         await state.set_state(CustomPostMenuState.custom_post)
#         year, month = datetime.now().year, datetime.now().month
#         await message.answer(
#             f"📅Выберите день и время: ",
#             reply_markup=create_calendar(
#                 year,
#                 month,
#             ),
#         )
#         await send_calendar_inline_kb()
#     elif message.text == "Очистить всю отложку":
#         await message.answer(
#             text="Вы уверены, что хотите удалить ВСЕ отложенные посты?",
#             reply_markup=get_keyboard("Да", "Назад"),
#         )

#         await state.set_state(DelayedMenuStates.delayed_clear)


# @delayed_menu_router.message(
#     F.text == "Да", StateFilter(DelayedMenuStates.delayed_clear)
# )
# async def clear_delayed_posts(message: types.Message, state: FSMContext):
#     scheduler_app.remove_all_jobs(scheduler)
#     await message.answer("Удалил все посты из отложки")
#     await delayed_menu(message)


# @delayed_menu_router.message(StateFilter(DelayedMenuStates.delayed_change))
# async def get_delayed_id(message: types.Message, state: FSMContext):
#     global delayed_id
#     await state.set_state(DelayedMenuStates.delayed_change_date)
#     delayed_id = message.text
#     year, month = datetime.now().year, datetime.now().month
#     await message.answer(
#         f"📅Выберите день и время: ",
#         reply_markup=create_calendar(
#             year,
#             month,
#         ),
#     )


# @delayed_menu_router.message(StateFilter(DelayedMenuStates.delayed_change_date))
# async def change_post_delayed_time(message: types.Message, state: FSMContext):
#     data = {
#         "job_id": delayed_id,
#         "custom_month": calendar_month,
#         "custom_day": calendar_day,
#         "custom_hour": calendar_hour,
#         "custom_minute": calendar_minute,
#     }
#     scheduler_app.reschedule_post(data, scheduler)
#     await message.answer("Изменил")
#     await delayed_menu(message)


# @delayed_menu_router.message(StateFilter(DelayedMenuStates.delayed_delete))
# async def delete_delayed_post(message: types.Message, state: FSMContext):
#     delayed_id = message.text
#     scheduler_app.delete_job(delayed_id, scheduler)
#     await state.finish()
#     await delayed_menu(message)
