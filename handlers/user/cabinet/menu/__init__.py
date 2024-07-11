from aiogram import Router, F
from handlers.user.cabinet.menu import handlers
from handlers.common.helper import Handler
from state.user import UserCabinetStates


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.main_handlers, [UserCabinetStates.waiting_menu, F.text]),
    ]

    inline_list = [
        Handler(handlers.show_history_order, [UserCabinetStates.waiting_history_order]),
    ]

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    for inline in inline_list:
        router.inline_query.register(inline.handler, *inline.filters)

    return router

