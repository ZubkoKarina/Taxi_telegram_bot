import re

from aiogram import types
from aiogram.filters import BaseFilter


class ValidNameFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        pattern = "^[a-zA-Zа-яА-ЯёЁіїІЇєЄґҐ]+\s[a-zA-Zа-яА-ЯёЁіїІЇєЄґҐ]+$"
        msg = message.text

        if bool(re.match(pattern, msg)) and msg.istitle():
            return True

        return False


class ValidFullNameFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        pattern = "^[а-яА-ЯёЁіїІЇєЄґҐ]+\s[а-яА-ЯёЁіїІЇєЄґҐ]+\s[а-яА-ЯёЁіїІЇєЄґҐ]+$"
        msg = message.text

        if bool(re.match(pattern, msg)) and msg.istitle():
            return True

        return False

