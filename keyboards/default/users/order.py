from keyboards.default.consts import DefaultConstructor
from texts.keyboards import OPEN_MENU
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS


order_kb = DefaultConstructor.create_kb(
    actions=[
        {'text': 'Замовити таксі 🚕', 'web_app': WebAppInfo(url=WEB_APP_ADDRESS)},
        OPEN_MENU,
    ], schema=[1, 1])


