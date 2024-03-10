from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.utils.markdown import hcode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.admin_filter import IsAdmin
from handlers.dayvinchik import sender
from start_menu import StartMenuStates
import old.scheduler_app as scheduler_app
from keyboards.reply import get_keyboard
from database import service_db
from delayed_menu import DelayedMenuStates

main_menu_router = Router()
main_menu_router.message.filter(IsAdmin())


class MainMenuStates(StatesGroup):
    sender = StatesGroup()
    parser = StatesGroup()


# @main_menu_router.message(Filters.text("Запостить") & Filters.state(States.custom_post_menu))


@main_menu_router.message(F.text == "Листать посты", StateFilter("*"))
async def select_posts(message: types.Message, state: FSMContext):
    await state.set_state(StartMenuStates.start)
    # scrapy.wbparse()
    await message.reply(
        "Высылаю посты",
        reply_markup=get_keyboard(
            "Запостить", "Скип", "Назад", placeholder="Действие", sizes=(3,)
        ),
    )
    await sender(message=message)


@main_menu_router.message(F.text == "Отложка", StateFilter("*"))
async def delayed_menu(message: types.Message, state: FSMContext):
    delayed_menu_keyboard = get_keyboard(
        "Изменить время",
        "Удалить пост",
        "Кастомный пост",
        "Очистить всю отложку",
        "Назад",
        sizes=(2, 2, 1),
    )
    await state.set_state(DelayedMenuStates.delayed_menu)
    delayed_post = scheduler_app.get_delayed_posts(scheduler)
    if delayed_post:
        delayed_posts = ""
        for delayed in delayed_post:
            jobname = delayed["jobname"]
            jobtime = delayed["jobtime"]
            jobid = delayed["job_id"]
            delayed_posts += f"{jobname}\n{jobtime}\n{hcode(jobid)}\n{'='*32}\n"

        await message.answer(
            text=delayed_posts, parse_mode="HTML", reply_markup=delayed_menu_keyboard
        )
    elif delayed_post == []:
        await message.answer(text="Отложка пустая", reply_markup=delayed_menu_keyboard)


@main_menu_router.message(F.text == "Парсер", StateFilter("*"))
async def ask_for_parser(message: types.Message, state: FSMContext):

    message_text = f"Вызываю парсер?\nСейчас в базе данных {len(service_db.get_all_products())} товаров"
    await message.answer(
        message_text, reply_markup=get_keyboard("Вызвать парсер", "Назад")
    )
    await state.set_state(MainMenuStates.parser)


@main_menu_router.message(
    F.text == "Вызвать парсер", StateFilter(MainMenuStates.parser), run_task=True
)
async def call_parser(message: types.Message, state: FSMContext):
    await message.answer(text="Вызвал, подождите пару минут.")
    posts_num = await main(skidka_link, table_name=wb_table_name)
    await message.answer(text=f"Сделано, число постов: {posts_num}")
    await main_menu(message)
    await state.finish() # Вроде set state none
