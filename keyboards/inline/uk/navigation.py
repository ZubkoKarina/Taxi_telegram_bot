from keyboards.inline.consts import InlineConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.uk import keyboards


def generation_buttons_navigation(google_url: str, waze_url: str):

    choice_type_navigation = InlineConstructor.create_kb(
        actions=[{
            'text': keyboards.OPEN_STANDARD_METHOD_NAVIGATION,
            'url': google_url,
        },
        {
            'text': keyboards.OPEN_WAZE_METHOD_NAVIGATION,
            'url': waze_url,
        },],
        schema=[1, 1]
    )
    return choice_type_navigation
