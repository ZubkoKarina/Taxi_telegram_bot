from keyboards.inline.consts import InlineConstructor
from texts.uk import keyboards

open_menu = InlineConstructor.create_kb(
    actions=[
        {
            'text': keyboards.TO_MENU,
            'callback_data': 'cabinet_menu'
        },
    ],
    schema=[1]
)