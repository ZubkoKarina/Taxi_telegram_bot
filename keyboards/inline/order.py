from keyboards.inline.consts import InlineConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS

open_web_app_order_kb = InlineConstructor.create_kb(
    actions=[{
        'text': 'Замовити таксі 🚕',
        'web_app': WebAppInfo(url=WEB_APP_ADDRESS),
    }],
    schema=[1]
)

