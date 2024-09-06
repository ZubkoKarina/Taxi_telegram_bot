from keyboards.inline.consts import InlineConstructor
from texts.uk import keyboards

choose_order = InlineConstructor.create_kb(
    actions=[{
        'text': keyboards.OPEN_HISTORY_ORDER,
        'switch_inline_query_current_chat': 'order_history_carousel',
        },
        {
            'text': keyboards.TO_MENU,
            'callback_data': 'cabinet_menu'
        },
    ],
    schema=[1, 1]
)
