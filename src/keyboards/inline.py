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
