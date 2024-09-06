from keyboards.default.consts import DefaultConstructor
from aiogram import types
from data.config import WEBHOOK_ADDRESS
from texts.en import keyboards

menu = DefaultConstructor.create_kb(
    actions=[
        keyboards.DEACTIVATE_DRIVER,
        keyboards.INFO,
        keyboards.HISTORY_ORDER,
        keyboards.SETTING,
    ], schema=[2, 2])


inactive_menu = DefaultConstructor.create_kb(
    actions=[
        keyboards.ACTIVATE_DRIVER,
        keyboards.INFO,
        keyboards.HISTORY_ORDER,
        keyboards.SETTING,
    ], schema=[2, 2])


