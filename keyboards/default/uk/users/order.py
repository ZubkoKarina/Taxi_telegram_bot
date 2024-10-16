from keyboards.default.consts import DefaultConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.uk import keyboards

web_app = DefaultConstructor.create_kb(
    actions=[
        {'text': keyboards.ORDER_TAXI, 'web_app': WebAppInfo(url=WEB_APP_ADDRESS)},
        keyboards.OPEN_MENU,
    ], schema=[1, 1])

order_menu = DefaultConstructor.create_kb(
    actions=[
        keyboards.CANCEL_ORDER,
        keyboards.CHAT_WITH_DRIVER,
    ], schema=[1, 1]
)

search_driver = DefaultConstructor.create_kb(
    actions=[
        keyboards.CHANGE_PRICE,
        keyboards.CANCEL_ORDER,
    ], schema=[1, 1]
)

no_search_driver = DefaultConstructor.create_kb(
    actions=[
        keyboards.SEARCH_AGAIN,
        keyboards.CHANGE_PRICE,
        keyboards.OPEN_MENU
    ],
    schema=[2, 1]
)

pre_order = DefaultConstructor.create_kb(
    actions=[
        keyboards.ACCEPT,
        keyboards.BACK
    ],
    schema=[1, 1]
)

menu_before_order = DefaultConstructor.create_kb(
    actions=[
        keyboards.STANDARD_ORDER,
        keyboards.PLANNED_ORDER,
        keyboards.OPEN_MENU,
    ], schema=[1, 2])

order_processing = DefaultConstructor.create_kb(
    actions=[
        keyboards.REPLACE_COST,
    ],
    schema=[1]
)

