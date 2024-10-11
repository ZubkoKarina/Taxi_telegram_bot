from aiogram import types
from aiogram.filters import BaseFilter
from datetime import datetime

class ValidDateFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        date_format = "%d.%m.%Y"
        msg = message.text

        try:
            entered_date = datetime.strptime(msg, date_format).date()
            if entered_date >= datetime.now().date():
                return True
            return False
        except ValueError:
            return False


class ValidTimeFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        time_format = "%H:%M"
        msg = message.text

        try:
            entered_time = datetime.strptime(msg, time_format).time()
            return True
        except ValueError:
            return False