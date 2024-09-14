from aiogram import Router, F
from handlers.user.cabinet.order import handlers
from handlers.common.helper import Handler, CallbackDataContainsKey
from state.user import OrderTaxi
from handlers.user.cabinet.common import callback_open_menu
from texts import filter_text


def prepare_router() -> Router:
    router = Router()
    message_list = [
        Handler(handlers.ask_open_order, [OrderTaxi.waiting_accept_city, filter_text('YES')]),
        Handler(handlers.ask_city, [OrderTaxi.waiting_accept_city, filter_text('NO')]),
        Handler(handlers.output_pre_order, [OrderTaxi.waiting_accept_city, filter_text('PRE_ORDER')]),
        Handler(handlers.create_pre_order, [OrderTaxi.waiting_create_pre_order, filter_text('ACCEPT')]),
        Handler(handlers.ask_open_order, [OrderTaxi.waiting_create_pre_order, filter_text('BACK')]),
        Handler(handlers.edit_city, [OrderTaxi.waiting_new_city, F.text]),
        Handler(handlers.create_order, [OrderTaxi.waiting_order_data, F.web_app_data]),
        Handler(handlers.order_menu, [OrderTaxi.waiting_menu_order]),
        Handler(handlers.take_cost, [OrderTaxi.waiting_new_price]),
        Handler(handlers.open_order_menu, [OrderTaxi.waiting_message_to_driver, filter_text('BACK')]),
        Handler(handlers.send_message_to_driver, [OrderTaxi.waiting_message_to_driver, F.text]),
        Handler(handlers.cancel_order, [OrderTaxi.waiting_cancel_order, filter_text('YES')]),
        Handler(handlers.open_order_menu, [OrderTaxi.waiting_cancel_order, filter_text('NO')])
    ]

    callback_list = [
        Handler(
            handlers.callback_message_to_driver, [OrderTaxi.waiting_menu_order, F.data == 'chat_with_driver']
        ),
        Handler(
            callback_open_menu, [OrderTaxi.waiting_order_data, F.data == 'cabinet_menu']
        ),
        Handler(
            handlers.rate_driver, [OrderTaxi.waiting_rate_driver, CallbackDataContainsKey('rate')]
        ),

    ]

    for callback in callback_list:
        router.callback_query.register(callback.handler, *callback.filters)

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router
