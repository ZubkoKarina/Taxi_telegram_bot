from aiogram import Router, F
from handlers.driver.cabinet.setting import handlers
from handlers.common.helper import Handler
from state.driver import EditDriver
from texts import filter_text


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.open_menu, [EditDriver.waiting_edit_menu, filter_text('OPEN_MENU')]),
        Handler(handlers.edit_name, [EditDriver.waiting_edit_menu, filter_text('EDIT_NAME')]),
        Handler(handlers.edit_city, [EditDriver.waiting_edit_menu, filter_text('EDIT_CITY')]),
        Handler(handlers.edit_region, [EditDriver.waiting_edit_menu, filter_text('EDIT_REGION')]),
        Handler(handlers.confirm_name, [EditDriver.waiting_name, F.text]),
        Handler(handlers.confirm_region, [EditDriver.waiting_region, F.text]),
        Handler(handlers.confirm_city, [EditDriver.waiting_city, F.text])
    ]

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

