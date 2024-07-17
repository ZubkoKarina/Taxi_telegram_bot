from keyboards.inline.consts import InlineConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.keyboards import TO_MENU

order_kb_inline = InlineConstructor.create_kb(
    actions=[{
        'text': 'Замовити таксі 🚕',
        'web_app': WebAppInfo(url=WEB_APP_ADDRESS),
    },
        {
        'text': TO_MENU,
        'callback_data': 'cabinet_menu'
    }],
    schema=[1, 1]
)

