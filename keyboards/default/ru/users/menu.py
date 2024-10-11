from keyboards.default.consts import DefaultConstructor
from aiogram import types
from data.config import WEB_APP_ADDRESS
from texts.ru import keyboards

menu_properties = {
    "order_taxi": types.WebAppInfo(url=WEB_APP_ADDRESS),
    "share_chatbot": ""
}

menu = DefaultConstructor.create_kb(
    actions=[
        keyboards.ORDER_TAXI,
        keyboards.HISTORY_ORDER,
        keyboards.SETTING,
        keyboards.SHARE_CHATBOT,
        keyboards.OTHER,
        keyboards.RELOAD
    ], schema=[1, 2, 2, 1])


