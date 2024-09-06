from keyboards.default.consts import DefaultConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.en import keyboards

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
        keyboards.CHANGE_PRICE
    ],
    schema=[1, 1]
)


