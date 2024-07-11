from aiogram import Router, F
from handlers.user.cabinet.edit_user import handlers
from handlers.common.helper import Handler
from state.user import EditUserInfo
from texts.keyboards import EDIT_NAME, OPEN_MENU


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.open_menu, [EditUserInfo.waiting_edit_info, F.text == OPEN_MENU]),
        Handler(handlers.edit_name, [EditUserInfo.waiting_edit_info, F.text == EDIT_NAME]),
        Handler(handlers.confirm_name, [EditUserInfo.waiting_name, F.text])
    ]

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

