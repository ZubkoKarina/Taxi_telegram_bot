from keyboards.default.consts import DefaultConstructor
from texts.keyboards import BECOME_PARTNER, REPORT_ISSUE, OPEN_MENU

other_kb = DefaultConstructor.create_kb(
    actions=[
        OPEN_MENU,
        BECOME_PARTNER,
        REPORT_ISSUE,
    ], schema=[2, 1])


