from keyboards.default.consts import DefaultConstructor
from texts.keyboards import OPEN_MENU, EDIT_NAME

edit_user = DefaultConstructor.create_kb(
    actions=[
        OPEN_MENU,
        EDIT_NAME,
    ], schema=[2])


