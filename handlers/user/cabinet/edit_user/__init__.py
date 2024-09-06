from aiogram import Router, F
from handlers.user.cabinet.edit_user import handlers
from handlers.common.helper import Handler
from state.user import EditUserInfo
from texts import filter_text
from handlers import validation
from filters.valid_name import ValidNameFilter


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.open_menu, [EditUserInfo.waiting_edit_info, filter_text('OPEN_MENU')]),
        Handler(handlers.edit_name, [EditUserInfo.waiting_edit_info, filter_text('EDIT_NAME')]),
        Handler(handlers.edit_city, [EditUserInfo.waiting_edit_info, filter_text('EDIT_CITY')]),
        Handler(handlers.edit_region, [EditUserInfo.waiting_edit_info, filter_text('EDIT_REGION')]),
        Handler(handlers.edit_language, [EditUserInfo.waiting_edit_info, filter_text('EDIT_LANGUAGE')]),
        Handler(handlers.confirm_name, [EditUserInfo.waiting_name, ValidNameFilter()]),
        Handler(handlers.confirm_region, [EditUserInfo.waiting_region, F.text]),
        Handler(handlers.confirm_city, [EditUserInfo.waiting_city, F.text])
    ]

    callback_list = [
        Handler(
            handlers.init_language, [EditUserInfo.waiting_language, F.data == 'en_language']
        ),
        Handler(
            handlers.init_language, [EditUserInfo.waiting_language, F.data == 'uk_language']
        ),
        Handler(
            handlers.init_language, [EditUserInfo.waiting_language, F.data == 'ru_language']
        ),
    ]

    validation_list = [
        Handler(validation.not_valid_text, [EditUserInfo.waiting_name]),
    ]

    for message in [*message_list, *validation_list]:
        router.message.register(message.handler, *message.filters)

    for callback in callback_list:
        router.callback_query.register(callback.handler, *callback.filters)

    return router

