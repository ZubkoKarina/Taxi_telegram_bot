from keyboards.default.consts import DefaultConstructor
from texts.en import keyboards

other = DefaultConstructor.create_kb(
    actions=[
        keyboards.OPEN_MENU,
        keyboards.BECOME_PARTNER,
        keyboards.REPORT_ISSUE,
    ], schema=[2, 1])


