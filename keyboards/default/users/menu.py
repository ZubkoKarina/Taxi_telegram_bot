from keyboards.default.consts import DefaultConstructor
from aiogram import types
from data.config import WEB_APP_ADDRESS

user_menu_text = {
    "order_taxi": 'Замовити таксі 🚕',
    "history_order": 'Історія поїзок 🕔',
    "setting": "Налаштування ⚙️",
    "share_chatbot": "Поділитися чат-ботом 🤝️",
    "reference_info": "Інше 🧩",
}

user_menu_properties = {
    "order_taxi": types.WebAppInfo(url=WEB_APP_ADDRESS),
    "share_chatbot": ""
}

user_menu_kb = DefaultConstructor.create_kb(
    actions=[
        user_menu_text['order_taxi'],
        user_menu_text['history_order'],
        user_menu_text['setting'],
        user_menu_text['share_chatbot'],
        user_menu_text['reference_info'],
    ], schema=[1, 2, 2])


