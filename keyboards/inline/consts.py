from typing import Type, TypeVar

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LoginUrl,
)

from ..keyboard_utils import schema_generator

A = TypeVar("A", bound=Type[CallbackData])


class InlineConstructor:
    aliases = {"cb": "callback_data"}

    available_properties = [
        "text",
        "callback_data",
        "url",
        "login_url",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "callback_game",
        "pay",
        "web_app"
    ]
    properties_amount = 2

    @staticmethod
    def create_kb(
            actions: list[
                dict[str, str | bool | A | LoginUrl]
            ],
            schema: list[int],
    ) -> InlineKeyboardMarkup:
        buttons: list[InlineKeyboardButton] = []

        for a in actions:
            data: dict[str, str | bool | A | LoginUrl] = {}

            for k, v in InlineConstructor.aliases.items():
                if k in a:
                    a[v] = a[k]
                    del a[k]

            for k in a:
                if k in InlineConstructor.available_properties:
                    if len(data) <= InlineConstructor.properties_amount:
                        data[k] = a[k]
                    else:
                        break

            if "callback_data" in data:
                if isinstance(data["callback_data"], CallbackData):
                    data["callback_data"] = data["callback_data"].pack()

            if len(data) != InlineConstructor.properties_amount:
                raise ValueError("Недостаточно данных для создания кнопки")

            buttons.append(InlineKeyboardButton(**data))

        kb = InlineKeyboardMarkup(
            inline_keyboard=schema_generator.create_keyboard_layout(buttons, schema)
        )
        return kb
