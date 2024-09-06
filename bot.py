from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from services.redis import redis_storage
from data.config import BOT_TOKEN
from middlewares.language_middleware import LanguageMiddleware

dp = Dispatcher(storage=redis_storage)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))