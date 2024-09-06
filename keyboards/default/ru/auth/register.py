from keyboards.default.consts import DefaultConstructor
from texts.ru import keyboards

phone_share = DefaultConstructor.create_kb(
    actions=[{"text": keyboards.SHARE_CONTACT, "contact": True}], schema=[1]
)
