from aiogram import types


def get_start_kb() -> types.ReplyKeyboardMarkup:
    start_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_kb.add(
        types.KeyboardButton("Одежда тпшкам"),
        types.KeyboardButton("Для дома"),
        types.KeyboardButton("Бижутерия"),
        types.KeyboardButton("Косметика"),
    )
    return start_kb


def get_main_kb() -> types.ReplyKeyboardMarkup:
    main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_kb.add(
        types.KeyboardButton("Листать посты"),
        types.KeyboardButton("Отложка"),
        types.KeyboardButton("Парсер"),
        types.KeyboardButton("Категории"),
    )
    return main_kb


def get_second_kb() -> types.ReplyKeyboardMarkup:
    second_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    second_kb.add(
        types.KeyboardButton("Запостить"),
        types.KeyboardButton("Скип"),
        types.KeyboardButton("Назад"),
    )
    return second_kb


def get_third_kb() -> types.ReplyKeyboardMarkup:
    third_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    third_kb.add(
        types.KeyboardButton("Изменить время"),
        types.KeyboardButton("Удалить пост"),
        types.KeyboardButton("Назад"),
    )
    return third_kb
