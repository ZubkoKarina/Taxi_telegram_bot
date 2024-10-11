from keyboards.default.consts import DefaultConstructor
from texts.ru import keyboards

money_transferred = DefaultConstructor.create_kb(
    actions=[
        keyboards.MONEY_TRANSFERRED,
        keyboards.OPEN_MENU
    ], schema=[1, 1])