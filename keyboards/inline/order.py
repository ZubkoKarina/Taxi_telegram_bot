from keyboards.inline.consts import InlineConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.keyboards import TO_MENU, REPLY_THE_MESSAGE
import json

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


def create_take_order_inline(info_order: dict):
    info_order = json.dumps(info_order)

    take_order_inline = InlineConstructor.create_kb(
        actions=[{
            'text': 'Прийняти ✅',
            'callback_data': info_order
        },
            {
                'text': 'Пропустити 🚫',
                'callback_data': 'skip_order'
            }],
        schema=[2]
    )
    return take_order_inline


def create_kb_for_payment_inline(payment_url: str):

    kb_for_payment_inline = InlineConstructor.create_kb(
        actions=[{
            'text': 'Оплатити 💳',
            'url': payment_url,
        },
        ],
        schema=[1]
    )
    
    return kb_for_payment_inline


rate = InlineConstructor.create_kb(
    actions=[{
        'text': '1',
        'callback_data': json.dumps({'rate': 1})
        },
        {
            'text': '2',
            'callback_data': json.dumps({'rate': 2})
        },
        {
            'text': '3',
            'callback_data': json.dumps({'rate': 3})
        },
        {
            'text': '4',
            'callback_data': json.dumps({'rate': 4})
        },
        {
            'text': '5',
            'callback_data': json.dumps({'rate': 5})
        },
    ],
    schema=[5]
)

reply_message_to_driver = InlineConstructor.create_kb(
    actions=[{
            'text': REPLY_THE_MESSAGE,
            'callback_data': 'chat_with_driver'
        }],
    schema=[1]
)
