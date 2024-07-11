from aiogram import Router, F
from handlers.user.cabinet.other import handlers
from handlers.common.helper import Handler
from state.user import OtherFun
from texts.keyboards import EDIT_NAME, OPEN_MENU


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.open_menu, [OtherFun.waiting_other_fun, F.text == OPEN_MENU]),
    ]

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

