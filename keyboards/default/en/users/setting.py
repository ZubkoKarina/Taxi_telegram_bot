from keyboards.default.consts import DefaultConstructor
from texts.en import keyboards

edit_user = DefaultConstructor.create_kb(
    actions=[
        keyboards.EDIT_NAME,
        keyboards.EDIT_CITY,
        keyboards.EDIT_REGION,
        keyboards.EDIT_LANGUAGE,
        keyboards.OPEN_MENU,
    ], schema=[2, 2, 1])


