from aiogram import Router, F
from handlers.driver.cabinet.menu import handlers
from handlers.common.helper import Handler
from state.driver import DriverCabinetStates
from handlers.driver.cabinet.common import callback_open_menu


def prepare_router() -> Router:

    router = Router()
    # Start
    message_list = [
        Handler(handlers.access_to_line, [DriverCabinetStates.waiting_geo, F.location]),
        Handler(handlers.main_handlers, [DriverCabinetStates.waiting_menu, F.text]),
        Handler(handlers.pass_fun, [DriverCabinetStates.waiting_history_order, F.text]),
    ]
    inline_list = [
        Handler(handlers.show_history_order, [DriverCabinetStates.waiting_history_order]),
    ]
    edit_message_list = [
        Handler(handlers.tracking_location, [F.location]),
    ]
    callback_list = [
        Handler(
            callback_open_menu, [DriverCabinetStates.waiting_history_order, F.data == 'cabinet_menu']
        )
    ]
    for message in message_list:
        router.message.register(message.handler, *message.filters)

    for message in edit_message_list:
        router.edited_message.register(message.handler, *message.filters)
    for callback in callback_list:
        router.callback_query.register(callback.handler, *callback.filters)

    for inline in inline_list:
        router.inline_query.register(inline.handler, *inline.filters)

    return router

