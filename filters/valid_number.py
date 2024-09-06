import re

from aiogram import types
from aiogram.filters import BaseFilter


class ValidNumberFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        pattern = "[0-9]+$"
        msg = message.text

        if bool(re.match(pattern, msg)):
            return True

        return False
