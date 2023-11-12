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
        types.KeyboardButton("Очистка БД"),
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
        types.KeyboardButton("Кастомный пост"),
        types.KeyboardButton("Назад"),
    )
    return third_kb


def get_clear_db_kb() -> types.ReplyKeyboardMarkup:
    clear_db_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clear_db_kb.add(
        types.KeyboardButton("Очистить ВБ БД"),
        types.KeyboardButton("Очистить ТГ БД"),
        types.KeyboardButton("Назад"),
    )
    return clear_db_kb


def get_parser_kb() -> types.ReplyKeyboardMarkup:
    parser_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    parser_kb.add(
        types.KeyboardButton("Вызвать парсер"),
        types.KeyboardButton("Назад"),
    )
    return parser_kb
