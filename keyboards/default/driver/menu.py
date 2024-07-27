from keyboards.default.consts import DefaultConstructor
from aiogram import types
from data.config import WEBHOOK_ADDRESS

driver_menu_text = {
    "list_order": 'Список Замовлень 🚕',
    "info": "Моя Інформація️ 👤",
    "history_order": 'Історія поїзок 🕔',
    "setting": "Налаштування ⚙️",
    "reference_info": "Інше 🧩",
    "deactivate": "Зійти з лінії 🪫",
    "activate": "Стати на лінію 🚖",
}

driver_menu_kb = DefaultConstructor.create_kb(
    actions=[
        {'text': driver_menu_text['list_order']},
        driver_menu_text['info'],
        driver_menu_text['history_order'],
        driver_menu_text['deactivate'],
        driver_menu_text['setting'],
    ], schema=[1, 2, 2])


inactive_driver_menu_kb = DefaultConstructor.create_kb(
    actions=[
        driver_menu_text['activate'],
        driver_menu_text['info'],
        driver_menu_text['history_order'],
        driver_menu_text['setting'],
    ], schema=[2, 2])


