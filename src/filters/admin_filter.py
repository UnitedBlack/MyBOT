from aiogram.filters import Filter
from aiogram import Bot, types


class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in bot.admins_list
