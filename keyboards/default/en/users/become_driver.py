from keyboards.default.consts import DefaultConstructor
from texts.en import keyboards

become_driver = DefaultConstructor.create_kb(
    actions=[
        keyboards.ALL_TRUE,
        keyboards.OPEN_MENU,
    ], schema=[1, 1])


