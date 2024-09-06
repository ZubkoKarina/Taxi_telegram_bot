from keyboards.inline.consts import InlineConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.en import keyboards
import json

web_app = InlineConstructor.create_kb(
    actions=[{
        'text': keyboards.ORDER_TAXI,
        'web_app': WebAppInfo(url=WEB_APP_ADDRESS),
    },
        {
            'text': keyboards.TO_MENU,
            'callback_data': 'cabinet_menu'
        }],
    schema=[1, 1]
)


def generation_notification_driver(info_order: dict):
    info_order = json.dumps(info_order)

    take_order_inline = InlineConstructor.create_kb(
        actions=[{
            'text': keyboards.ACCEPT,
            'callback_data': info_order
        },
            {
                'text': keyboards.SKIP,
                'callback_data': 'skip_order'
            }],
        schema=[2]
    )
    return take_order_inline


def generation_button_payment(payment_url: str):

    kb_for_payment_inline = InlineConstructor.create_kb(
        actions=[{
            'text': keyboards.PAY,
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
            'text': keyboards.REPLY_THE_MESSAGE,
            'callback_data': 'chat_with_driver'
        }],
    schema=[1]
)
