from aiogram import Router, F
from handlers.user.cabinet.order import search_driver, create_order, pre_order, standard_order, menu_order, planned_order
from handlers.common.helper import Handler, CallbackDataContainsKey
from handlers.user.cabinet.order.menu_order import order_menu
from state.user import OrderTaxi, PlannedOrderTaxi
from handlers.user.cabinet.common import callback_open_menu
from texts import filter_text
from filters.valid_date import ValidDateFilter, ValidTimeFilter

def prepare_router() -> Router:
    router = Router()
    message_list_main = [
        Handler(create_order.create_order, [OrderTaxi.waiting_order_data, F.web_app_data]),
        Handler(create_order.open_menu, [filter_text('OPEN_MENU')]),
    ]

    message_list_order_menu = [
        Handler(menu_order.order_menu, [OrderTaxi.waiting_menu_order]),
        Handler(menu_order.take_cost, [OrderTaxi.waiting_new_price]),
        Handler(menu_order.open_order_menu, [OrderTaxi.waiting_message_to_driver, filter_text('BACK')]),
        Handler(menu_order.send_message_to_driver, [OrderTaxi.waiting_message_to_driver, F.text]),
        Handler(menu_order.cancel_order, [OrderTaxi.waiting_cancel_order, filter_text('YES')]),
        Handler(menu_order.open_order_menu, [OrderTaxi.waiting_cancel_order, filter_text('NO')]),
        Handler(menu_order.take_replace_cost, [OrderTaxi.waiting_replace_cost, F.text]),
        Handler(menu_order.take_status_replace_cost, [OrderTaxi.waiting_accept_replace_cost, filter_text('YES')]),
        Handler(menu_order.take_status_replace_cost, [OrderTaxi.waiting_accept_replace_cost, filter_text('NO')]),
    ]

    message_list_standard_order = [
        Handler(standard_order.ask_confirm_city, [OrderTaxi.waiting_type_order, filter_text('STANDARD_ORDER')]),
        Handler(standard_order.ask_open_order, [OrderTaxi.waiting_accept_city, filter_text('YES')]),
        Handler(standard_order.ask_city, [OrderTaxi.waiting_accept_city, filter_text('NO')]),
        Handler(standard_order.edit_city, [OrderTaxi.waiting_new_city, F.text]),
    ]

    message_list_planned_order = [
        Handler(planned_order.asking_date_order, [OrderTaxi.waiting_type_order, filter_text('PLANNED_ORDER')]),
        Handler(planned_order.save_date_order, [PlannedOrderTaxi.waiting_date_order]),
        Handler(planned_order.save_time_order, [PlannedOrderTaxi.waiting_time_order]),
        Handler(planned_order.ask_open_order, [PlannedOrderTaxi.waiting_accept_city, filter_text('YES')]),
        Handler(planned_order.ask_city, [PlannedOrderTaxi.waiting_accept_city, filter_text('NO')]),
        Handler(planned_order.edit_city, [PlannedOrderTaxi.waiting_new_city, F.text]),
    ]

    message_list_pre_order = [
        Handler(standard_order.ask_open_order, [OrderTaxi.waiting_create_pre_order, filter_text('BACK')]),
        Handler(pre_order.asking_pre_order, [OrderTaxi.waiting_type_order, filter_text('PRE_ORDER')]),
        Handler(pre_order.create_pre_order, [OrderTaxi.waiting_create_pre_order, filter_text('ACCEPT')]),
    ]

    callback_list = [
        Handler(
            menu_order.callback_message_to_driver, [OrderTaxi.waiting_menu_order, F.data == 'chat_with_driver']
        ),
        Handler(
            callback_open_menu, [OrderTaxi.waiting_order_data, F.data == 'cabinet_menu']
        ),
        Handler(
            menu_order.rate_driver, [OrderTaxi.waiting_rate_driver, CallbackDataContainsKey('rate')]
        ),
        Handler(standard_order.ask_city, [OrderTaxi.waiting_type_order,  F.data == 'edit_city']),
        Handler(planned_order.ask_city, [PlannedOrderTaxi.waiting_accept_city, F.data == 'edit_city']),
    ]

    for callback in callback_list:
        router.callback_query.register(callback.handler, *callback.filters)

    for message in [*message_list_standard_order, *message_list_planned_order, *message_list_order_menu, *message_list_pre_order, *message_list_main]:
        router.message.register(message.handler, *message.filters)

    return router
