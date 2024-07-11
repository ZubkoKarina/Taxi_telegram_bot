from keyboards.inline.consts import InlineConstructor

choose_order = InlineConstructor.create_kb(
    actions=[{
        'text': 'Віткрити історію замовлень 📋',
        'switch_inline_query_current_chat': 'order_history_carousel',
    }],
    schema=[1]
)

