from keyboards.default.consts import DefaultConstructor
from texts.keyboards import OPEN_MENU, EDIT_NAME, EDIT_CITY

edit_user = DefaultConstructor.create_kb(
    actions=[
        EDIT_NAME,
        EDIT_CITY,
        OPEN_MENU,
    ], schema=[2, 1])


