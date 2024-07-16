from keyboards.inline.consts import InlineConstructor
from texts.keyboards import TO_MENU

choose_order = InlineConstructor.create_kb(
    actions=[{
        'text': 'Віткрити історію замовлень 📋',
        'switch_inline_query_current_chat': 'order_history_carousel',
        },
        {
            'text': TO_MENU,
            'callback_data': 'cabinet_menu'
        },
    ],
    schema=[1, 1]
)
