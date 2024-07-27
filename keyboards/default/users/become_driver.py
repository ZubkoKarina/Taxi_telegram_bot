from keyboards.default.consts import DefaultConstructor
from texts.keyboards import ALL_TRUE, OPEN_MENU

become_driver_kb = DefaultConstructor.create_kb(
    actions=[
        ALL_TRUE,
        OPEN_MENU,
    ], schema=[1, 1])


