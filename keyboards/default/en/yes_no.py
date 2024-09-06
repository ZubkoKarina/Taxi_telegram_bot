from keyboards.default.consts import DefaultConstructor
from texts.en import keyboards

yes_no = DefaultConstructor.create_kb(
    actions=[
        keyboards.YES,
        keyboards.NO,
    ], schema=[2])


