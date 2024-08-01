from keyboards.default.consts import DefaultConstructor
from texts.keyboards import OPEN_MENU, EDIT_NAME, EDIT_CITY, EDIT_REGION

edit_driver_kb = DefaultConstructor.create_kb(
    actions=[
        EDIT_NAME,
        EDIT_CITY,
        EDIT_REGION,
        OPEN_MENU,
    ], schema=[2, 2])


