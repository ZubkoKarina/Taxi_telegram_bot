from data import config
from keyboards.inline.consts import InlineConstructor
from keyboards.inline.consts import InlineConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.uk import keyboards
import json

share_chatbot = InlineConstructor.create_kb(
    actions=[
        {
            "text": keyboards.SHARE,
            "url": f"https://t.me/share/url?url={config.BOT_URL}"
        }
    ],
    schema=[1]
)