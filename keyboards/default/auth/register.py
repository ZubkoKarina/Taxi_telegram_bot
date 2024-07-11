from keyboards.default.consts import DefaultConstructor
from texts.keyboards import SHARE_CONTACT

phone_share_kb = DefaultConstructor.create_kb(
    actions=[{"text": SHARE_CONTACT, "contact": True}], schema=[1]
)
