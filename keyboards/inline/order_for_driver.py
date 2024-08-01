from keyboards.inline.consts import InlineConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.keyboards import (CANCEL_ORDER, DRIVER_ON_PLACE,
                             DRIVER_START_ORDER, DRIVER_END_ORDER, REPLY_THE_MESSAGE, CHAT_WITH_PASSENGER)
import json

driver_order_menu = InlineConstructor.create_kb(
    actions=[
        {
            'text': DRIVER_ON_PLACE,
            'callback_data': 'driver_on_place'
        },
        {
            'text': CHAT_WITH_PASSENGER,
            'callback_data': 'chat_with_passenger'
        },
        {
            'text': CANCEL_ORDER,
            'callback_data': 'cancel_order'
        }],
    schema=[1, 1, 1]
)

order_arrival_time = InlineConstructor.create_kb(
    actions=[{
        'text': '3 хв',
        'callback_data': json.dumps({'arrival_time': '3 хв'})
        },
        {
            'text': '5 хв',
            'callback_data': json.dumps({'arrival_time': '5 хв'})
        },
        {
            'text': '7 хв',
            'callback_data': json.dumps({'arrival_time': '7 хв'})
        },
        {
            'text': '10 хв',
            'callback_data': json.dumps({'arrival_time': '10 хв'})
        },
        {
            'text': '>10 хв',
            'callback_data': json.dumps({'arrival_time': '>10 хв'})
        },
    ],
    schema=[5]
)

driver_order_start = InlineConstructor.create_kb(
    actions=[{
        'text': DRIVER_START_ORDER,
        'callback_data': 'driver_start_order'
        },
        {
            'text': CHAT_WITH_PASSENGER,
            'callback_data': 'chat_with_passenger'
        },
        {
            'text': CANCEL_ORDER,
            'callback_data': 'cancel_order'
        },
    ],
    schema=[1, 1, 1]
)

driver_order_end = InlineConstructor.create_kb(
    actions=[
        {
            'text': DRIVER_END_ORDER,
            'callback_data': 'driver_end_order'
        }],
    schema=[1]
)

reply_message_to_passenger = InlineConstructor.create_kb(
    actions=[{
            'text': REPLY_THE_MESSAGE,
            'callback_data': 'chat_with_passenger'
        }],
    schema=[1]
)
