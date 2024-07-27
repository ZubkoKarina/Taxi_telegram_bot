from keyboards.default.consts import DefaultConstructor
from texts.keyboards import OPEN_MENU
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.keyboards import CANCEL_ORDER, ORDER_INFO, CHAT_WITH_DRIVER, CHANGE_PRICE, SEARCH_AGAIN

open_order_kb = DefaultConstructor.create_kb(
    actions=[
        {'text': 'Замовити таксі 🚕', 'web_app': WebAppInfo(url=WEB_APP_ADDRESS)},
        OPEN_MENU,
    ], schema=[1, 1])

order_menu_kb = DefaultConstructor.create_kb(
    actions=[
        CANCEL_ORDER,
        CHAT_WITH_DRIVER,
    ], schema=[1, 1]
)

order_search_driver_kb = DefaultConstructor.create_kb(
    actions=[
        CHANGE_PRICE,
        CANCEL_ORDER,
    ], schema=[1, 1]
)

order_no_search_driver_kb = DefaultConstructor.create_kb(
    actions=[
        SEARCH_AGAIN,
        CHANGE_PRICE
    ],
    schema=[1, 1]
)


