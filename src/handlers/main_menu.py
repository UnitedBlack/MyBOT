from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.utils.markdown import hcode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from filters.admin_filter import IsAdmin
from start_menu import StartMenuStates
import scheduler_app

main_menu_router = Router()
main_menu_router.message.filter(IsAdmin())

class MainMenuStates(StatesGroup):
    sender = StatesGroup()
    delayed_menu = StatesGroup()
    parser = StatesGroup()


# @main_menu_router.message(Filters.text("Запостить") & Filters.state(States.custom_post_menu))


@main_menu_router.message(F.text == "Листать посты", StateFilter("*"))
async def select_posts(message: types.Message, state: FSMContext):
    await state.set_state(StartMenuStates.start)
    # scrapy.wbparse()
    await message.reply("Высылаю посты", reply_markup=get_second_kb())
    await sender(message=message)


@main_menu_router.message(F.text == "Отложка", StateFilter("*"))
async def delayed_menu(message: types.Message, state: FSMContext):
    await States.delayed_menu.set()
    delayed_post = scheduler_app.get_delayed_posts(scheduler)
    if delayed_post:
        delayed_posts = ""
        for delayed in delayed_post:
            jobname = delayed["jobname"]
            jobtime = delayed["jobtime"]
            jobid = delayed["job_id"]
            delayed_posts += f"{jobname}\n{jobtime}\n{hcode(jobid)}\n{'='*32}\n"

        await bot.send_message(
            admin_id,
            text=delayed_posts,
            parse_mode="HTML",
            reply_markup=get_third_kb(),
        )
    elif delayed_post == []:
        await bot.send_message(
            admin_id, text="Отложка пустая", reply_markup=get_third_kb()
        )


@main_menu_router.message(F.text == "Парсер", StateFilter("*"))
async def ask_for_parser(message: types.Message, state: FSMContext):
    message_text = f"Вызываю парсер?\nСейчас в базе данных {scrapy.count_of_products_in_db()} товаров"
    await bot.send_message(admin_id, text=message_text, reply_markup=get_parser_kb())
    await States.parser.set()


@main_menu_router.message(
    F.text == "Вызвать парсер", StateFilter(MainMenuStates.parser), run_task=True
)
async def call_parser(message: types.Message, state: FSMContext):
    await bot.send_message(
        admin_id,
        text="Вызвал, подождите пару минут.",
    )
    posts_num = await main(skidka_link, table_name=wb_table_name)
    await bot.send_message(admin_id, text=f"Сделано, число постов: {posts_num}")
    await main_menu(message)
    await state.finish()
