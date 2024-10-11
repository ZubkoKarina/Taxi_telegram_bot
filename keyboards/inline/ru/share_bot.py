from data import config
from keyboards.inline.consts import InlineConstructor
from texts.ru import keyboards

share_chatbot = InlineConstructor.create_kb(
    actions=[
        {
            "text": keyboards.SHARE,
            "url": f"https://t.me/share/url?url={config.BOT_URL}"
        }
    ],
    schema=[1]
)