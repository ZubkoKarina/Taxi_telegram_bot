from keyboards.inline.consts import InlineConstructor
from aiogram.types import WebAppInfo
from data.config import WEB_APP_ADDRESS
from texts.ru import keyboards


def generation_buttons_navigation(location: dict):
    google_url = f'https://www.google.com/maps/dir/?api=1&destination={location.get("lat")},{location.get("lng")}&travelmode=driving'
    waze_url = f'https://www.waze.com/ul?ll={location.get("lat")},{location.get("lng")}&navigate=yes&zoom=17'

    choice_type_navigation = InlineConstructor.create_kb(
        actions=[{
            'text': keyboards.OPEN_STANDARD_METHOD_NAVIGATION,
            'url': google_url
        },
        {
            'text': keyboards.OPEN_WAZE_METHOD_NAVIGATION,
            'url': waze_url,
        },],
        schema=[1, 1]
    )
    return choice_type_navigation
