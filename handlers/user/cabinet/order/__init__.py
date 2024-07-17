from aiogram import Router, F
from handlers.user.cabinet.order import handlers
from handlers.common.helper import Handler
from state.user import OrderTaxi
from texts.keyboards import YES, NO, OPEN_MENU
from handlers.user.cabinet.common import callback_open_menu


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.ask_open_order, [OrderTaxi.waiting_accept_city, F.text == YES]),
        Handler(handlers.ask_city, [OrderTaxi.waiting_accept_city, F.text == NO]),
        Handler(handlers.edit_city, [OrderTaxi.waiting_new_city, F.text]),
        Handler(handlers.open_menu, [OrderTaxi.waiting_order_data, F.text == OPEN_MENU]),
        Handler(handlers.accept_order_data, [OrderTaxi.waiting_order_data, F.web_app_data]),
    ]

    callback_list = [
        Handler(
            callback_open_menu, [OrderTaxi.waiting_order_data, F.data == 'cabinet_menu']
        ),
    ]
    for callback in callback_list:
        router.callback_query.register(callback.handler, *callback.filters)

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

