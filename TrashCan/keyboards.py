from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        KeyboardButton(text="Запостить"),
        KeyboardButton(text="Скип")
    ],
    resize_keyboard=True,
    input_field_placeholder="Вб залупа"
)