from typing import Sequence, Dict

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType

from ..keyboard_utils import schema_generator


class DefaultConstructor:
    aliases = {
        "contact": "request_contact",
        "location": "request_location",
        "poll": "request_poll",
        "web": "web_app"
    }

    available_properties = [
        "text",
        "request_contact",
        "request_location",
        "request_poll",
        "request_user",
        "request_chat",
        "web_app",
    ]

    properties_amount = 1

    @staticmethod
    def create_kb(
            actions: Sequence[str | Dict[str, str | bool | KeyboardButtonPollType]],
            schema: Sequence[int],
            resize_keyboard: bool = True,
            selective: bool = False,
            one_time_keyboard: bool = False,
            is_persistent: bool = True,
    ) -> ReplyKeyboardMarkup:
        buttons: list[KeyboardButton] = []

        for a in actions:
            if isinstance(a, str):
                a = {"text": a}

            data: Dict[str, str | bool | KeyboardButtonPollType] = {}

            # Replace aliases
            for k, v in DefaultConstructor.aliases.items():
                if k in a:
                    a[v] = a[k]
                    del a[k]

            for k in a:
                if k in DefaultConstructor.available_properties:
                    if len(data) <= DefaultConstructor.properties_amount:
                        data[k] = a[k]
                    else:
                        break

            if len(data) < DefaultConstructor.properties_amount:
                raise ValueError("Недостаточно данных для создания кнопки")

            buttons.append(KeyboardButton(**data))

        kb = ReplyKeyboardMarkup(
            is_persistent=is_persistent,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
            selective=selective,
            keyboard=schema_generator.create_keyboard_layout(buttons, schema)
        )

        return kb
