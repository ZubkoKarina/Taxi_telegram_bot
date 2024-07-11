from keyboards.default.consts import DefaultConstructor
from texts.keyboards import YES, NO

yes_no_kb = DefaultConstructor.create_kb(
    actions=[
        YES,
        NO,
    ], schema=[2])


