from aiogram import Router, F
from handlers.driver.cabinet.order import handlers
from handlers.common.helper import Handler, CallbackDataContainsKey
from state.driver import OrderTaxi, DriverCabinetStates
from texts.keyboards import YES, NO, OPEN_MENU
from handlers.user.cabinet.common import callback_open_menu


def prepare_router() -> Router:

    router = Router()
    message_list = [
    ]
    callback_list = [
        Handler(
            handlers.accept_order, [DriverCabinetStates.waiting_menu, CallbackDataContainsKey('id')]
        ),
        Handler(
            handlers.take_arrival_time, [DriverCabinetStates.waiting_menu, CallbackDataContainsKey('arrival_time')]
        ),
        Handler(
            handlers.skip_order, [DriverCabinetStates.waiting_menu, F.data == 'skip_order']
        ),
        Handler(
            handlers.cancel_order, [DriverCabinetStates.waiting_menu, F.data == 'cancel_order']
        ),
        Handler(
            handlers.driver_in_place, [DriverCabinetStates.waiting_menu, F.data == 'driver_on_place']
        ),
        Handler(
            handlers.start_order, [DriverCabinetStates.waiting_menu, F.data == 'driver_start_order']
        ),
        Handler(
            handlers.end_order, [DriverCabinetStates.waiting_menu, F.data == 'driver_end_order']
        ),
        Handler(
            handlers.rate_passenger, [DriverCabinetStates.waiting_menu, CallbackDataContainsKey('rate')]
        )
    ]

    for callback in callback_list:
        router.callback_query.register(callback.handler, *callback.filters)

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

