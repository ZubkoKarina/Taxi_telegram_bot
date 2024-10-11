from keyboards.inline.consts import InlineConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.en import keyboards
import json

menu = InlineConstructor.create_kb(
    actions=[
        {
            'text': keyboards.DRIVER_ON_PLACE,
            'callback_data': 'driver_on_place'
        },
        {
            'text': keyboards.CHAT_WITH_PASSENGER,
            'callback_data': 'chat_with_passenger'
        },
        {
            'text': keyboards.OPEN_NAVIGATOR,
            'callback_data': 'open_navigation_from'
        },
        {
            'text': keyboards.REPLACE_COST,
            'callback_data': 'replace_cost'
        },
        {
            'text': keyboards.SOS,
            'callback_data': 'sos'
        },
        {
            'text': keyboards.CANCEL_ORDER,
            'callback_data': 'cancel_order'
        }],
    schema=[1, 2, 1, 2]
)

arrival_time = InlineConstructor.create_kb(
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

start = InlineConstructor.create_kb(
    actions=[{
        'text': keyboards.DRIVER_START_ORDER,
        'callback_data': 'driver_start_order'
        },
        {
            'text': keyboards.CHAT_WITH_PASSENGER,
            'callback_data': 'chat_with_passenger'
        },
        {
            'text': keyboards.OPEN_NAVIGATOR,
            'callback_data': 'open_navigation_to'
        },
        {
            'text': keyboards.REPLACE_COST,
            'callback_data': 'replace_cost'
        },
        {
            'text': keyboards.SOS,
            'callback_data': 'sos'
        },
        {
            'text': keyboards.CANCEL_ORDER,
            'callback_data': 'cancel_order'
        },
    ],
    schema=[1, 2, 1, 2]
)

end = InlineConstructor.create_kb(
    actions=[
        {
            'text': keyboards.DRIVER_END_ORDER,
            'callback_data': 'driver_end_order'
        },
        {
            'text': keyboards.REPLACE_COST,
            'callback_data': 'replace_cost'
        },
        {
            'text': keyboards.OPEN_NAVIGATOR,
            'callback_data': 'open_navigation_to'
        },
        {
            'text': keyboards.SOS,
            'callback_data': 'sos'
        },
    ],
    schema=[1, 1, 2]
)

end_with_additional_point = InlineConstructor.create_kb(
    actions=[
        {
            'text': keyboards.DRIVER_END_ORDER,
            'callback_data': 'driver_end_order'
        },
        {
            'text': keyboards.ADDITIONAL_POINT,
            'callback_data': 'additional_point'
        },
        {
            'text': keyboards.OPEN_NAVIGATOR,
            'callback_data': 'open_navigation_to'
        },
        {
            'text': keyboards.SOS,
            'callback_data': 'sos'
        },
        {
            'text': keyboards.REPLACE_COST,
            'callback_data': 'replace_cost'
        },
    ],
    schema=[1, 2, 2]
)

end_with_off_timer = InlineConstructor.create_kb(
    actions=[
        {
            'text': keyboards.DRIVER_END_ORDER,
            'callback_data': 'driver_end_order'
        },
        {
            'text': keyboards.OFF_TIMER,
            'callback_data': 'end_additional_point'
        },
        {
            'text': keyboards.OPEN_NAVIGATOR,
            'callback_data': 'open_navigation_to'
        },
        {
            'text': keyboards.REPLACE_COST,
            'callback_data': 'replace_cost'
        },
        {
            'text': keyboards.SOS,
            'callback_data': 'sos'
        },
    ],
    schema=[1, 2, 2]
)

reply_message_to_passenger = InlineConstructor.create_kb(
    actions=[{
            'text': keyboards.REPLY_THE_MESSAGE,
            'callback_data': 'chat_with_passenger'
        }],
    schema=[1]
)
