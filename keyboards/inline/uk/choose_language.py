from keyboards.inline.consts import InlineConstructor


choose_language = InlineConstructor.create_kb(
        actions=[{
            'text': 'UK 🇺🇦',
            'callback_data': 'uk_language'
        },
        {
            'text': "RU",
            'callback_data': 'ru_language'
        },
        {
            'text': 'EN 🇺🇸',
            'callback_data': 'en_language'
        },
        ],
        schema=[3]
    )