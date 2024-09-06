from aiogram import Router, F
from handlers.driver.cabinet.order import handlers
from handlers.common.helper import Handler, CallbackDataContainsKey
from state.driver import OrderDriver, DriverCabinetStates
from texts import filter_text
from handlers.user.cabinet.common import callback_open_menu


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(
            handlers.open_order_menu,
            [OrderDriver.waiting_message_to_passenger, filter_text('BACK')]
        ),
        Handler(
            handlers.send_message_to_passenger,
            [OrderDriver.waiting_message_to_passenger, F.text]
        ),
        Handler(
            handlers.cancel_order,
            [OrderDriver.waiting_cancel_order, filter_text('YES')]
        ),
        Handler(
            handlers.open_order_menu,
            [OrderDriver.waiting_cancel_order, filter_text('NO')]
        )
    ]
    callback_list = [
        Handler(
            handlers.accept_order, [CallbackDataContainsKey('id')]
        ),
        Handler(
            handlers.take_arrival_time, [CallbackDataContainsKey('arrival_time')]
        ),
        Handler(
            handlers.skip_order, [F.data == 'skip_order']
        ),
        Handler(
            handlers.sure_cancel_order, [F.data == 'cancel_order']
        ),
        Handler(
            handlers.driver_in_place, [F.data == 'driver_on_place']
        ),
        Handler(
            handlers.start_order, [F.data == 'driver_start_order']
        ),
        Handler(
            handlers.end_order, [F.data == 'driver_end_order']
        ),
        Handler(
            handlers.choice_type_navigation, [F.data == 'open_navigation_to']
        ),
        Handler(
            handlers.choice_type_navigation, [F.data == 'open_navigation_from']
        ),
        Handler(
            handlers.rate_passenger, [CallbackDataContainsKey('rate')]
        ),
        Handler(
            handlers.start_message_to_passenger, [F.data == 'chat_with_passenger']
        ),
    ]

    for callback in callback_list:
        router.callback_query.register(callback.handler, *callback.filters)

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

