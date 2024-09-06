from keyboards.default.consts import DefaultConstructor
from texts.ru import keyboards

edit_driver = DefaultConstructor.create_kb(
    actions=[
        keyboards.EDIT_NAME,
        keyboards.EDIT_CITY,
        keyboards.EDIT_REGION,
        keyboards.OPEN_MENU,
    ], schema=[2, 2])


