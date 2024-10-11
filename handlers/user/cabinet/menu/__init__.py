from aiogram import Router, F
from handlers.user.cabinet.menu import handlers
from handlers.common.helper import Handler
from state.user import UserCabinetStates
from handlers.user.cabinet.common import callback_open_menu


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.main_handlers, [UserCabinetStates.waiting_menu, F.text]),
        Handler(handlers.pass_fun, [UserCabinetStates.waiting_history_order, F.text]),
    ]

    inline_list = [
        Handler(handlers.show_history_order, [UserCabinetStates.waiting_history_order]),
    ]

    callback_list = [
        Handler(
            callback_open_menu, [UserCabinetStates.waiting_history_order, F.data == 'cabinet_menu']
        )
    ]

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    for callback in callback_list:
        router.callback_query.register(callback.handler, *callback.filters)

    for inline in inline_list:
        router.inline_query.register(inline.handler, *inline.filters)

    return router

