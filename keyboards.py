from aiogram import types
import calendar
import datetime
from configure_bot import month_names


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
        types.KeyboardButton("Очистить всю отложку"),
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


def get_approve_kb() -> types.ReplyKeyboardMarkup:
    clear_db_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clear_db_kb.add(
        types.KeyboardButton("Да"),
        types.KeyboardButton("Назад"),
    )
    return clear_db_kb


def create_calendar(year=None, month=None):
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    # Get the month name from the list
    month_name = month_names[month - 1]
    data_ignore = types.InlineKeyboardButton(
        month_name + " " + str(year), callback_data="ignore"
    )
    markup = types.InlineKeyboardMarkup(row_width=7)
    markup.row(
        *[
            types.InlineKeyboardButton(day, callback_data="ignore")
            for day in ["П", "В", "С", "Ч", "П", "С", "В"]
        ]
    )  # Days of Week
    for week in calendar.monthcalendar(year, month):
        row = []
        for day in week:
            if day == 0 or (day < now.day and month == now.month and year == now.year):
                row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                # If the day is the current day, add *
                if day == now.day and month == now.month and year == now.year:
                    row.append(
                        types.InlineKeyboardButton(
                            f"*{day}*", callback_data=f"calendar-{day}-{month}-{year}"
                        )
                    )
                else:
                    row.append(
                        types.InlineKeyboardButton(
                            str(day), callback_data=f"calendar-{day}-{month}-{year}"
                        )
                    )
        # If the row is not all empty, add it to the markup
        if any(button.text.strip() != "" for button in row):
            markup.row(*row)
    # Buttons for navigation
    if year > now.year or (year == now.year and month > now.month):
        markup.row(
            types.InlineKeyboardButton(
                "<<", callback_data=f"prev-month-{month}-year-{year}"
            ),
            data_ignore,
            types.InlineKeyboardButton(
                ">>", callback_data=f"next-month-{month}-year-{year}"
            ),
        )
    else:
        markup.row(
            types.InlineKeyboardButton(" ", callback_data="ignore"),
            data_ignore,
            types.InlineKeyboardButton(
                ">>", callback_data=f"next-month-{month}-year-{year}"
            ),
        )
    return markup


def create_time_kb() -> types.InlineKeyboardMarkup:
    time_kb = types.InlineKeyboardMarkup()
    row = []
    for hour in range(10, 23):
        row.append(
            types.InlineKeyboardButton(f"{hour}:00", callback_data=f"time-{hour}-00")
        )
        if hour != 22:
            row.append(
                types.InlineKeyboardButton(
                    f"{hour}:30", callback_data=f"time-{hour}-30"
                )
            )
        if len(row) >= 6:
            time_kb.row(*row)
            row = []
    if row:
        time_kb.row(*row)
    time_kb.row(types.InlineKeyboardButton("Назад", callback_data="back-time"))
    return time_kb
