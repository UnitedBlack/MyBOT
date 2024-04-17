from config import categories
from typing import Any, Callable, Awaitable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
import json

from logic.main.core import ScrapyCore

class ConfigurationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        message = json.loads(event.model_dump_json())
        message_text = message["message"]["text"]
        user_config = data.get("skidka_link")
        if not user_config and message_text in categories.keys():
            print("нет конфига")
            config_data = categories.get(message_text)
            data["skidka_link"] = config_data["skidka_category_link"]
            data["group_name"] = config_data["group_name"]
            data["scheduler"] = config_data["scheduler"]
            data["tg_group_id"] = config_data["tg_group_id"]
        return await handler(event, data)

# редис для сохранения конфигов

# async def get_user_config(user_id):
#     # Здесь должен быть код для получения конфигурации пользователя из базы данных или другого источника
#     pass


# async def define_user_configuration(user_id):
#     # Здесь должен быть код для определения конфигурации пользователя
#     pass


# async def save_user_config(user_id, config):
#     # Здесь должен быть код для сохранения конфигурации пользователя


# Добавление middleware в диспетчер
