from aiogram import Router, F
from handlers.driver.cabinet.menu import handlers
from handlers.common.helper import Handler
from state.driver import DriverCabinetStates


def prepare_router() -> Router:

    router = Router()
    # Start
    message_list = [
        Handler(handlers.access_to_line, [DriverCabinetStates.waiting_geo, F.location]),
        Handler(handlers.main_handlers, [DriverCabinetStates.waiting_menu, F.text]),
    ]

    edit_message_list = [
        Handler(handlers.tracking_location, [F.location]),
    ]
    for message in message_list:
        router.message.register(message.handler, *message.filters)

    for message in edit_message_list:
        router.edited_message.register(message.handler, *message.filters)

    return router

