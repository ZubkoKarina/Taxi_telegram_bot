from aiogram import Bot, Dispatcher

from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from data.config import (
    BOT_TOKEN
)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))