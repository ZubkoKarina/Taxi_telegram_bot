from aiogram import Router, F
from handlers.driver.cabinet.setting import handlers
from handlers.common.helper import Handler
from state.driver import EditDriver, TopUp
from texts import filter_text


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.open_menu, [EditDriver.waiting_edit_menu, filter_text('OPEN_MENU')]),
        Handler(handlers.edit_name, [EditDriver.waiting_edit_menu, filter_text('EDIT_NAME')]),
        Handler(handlers.edit_city, [EditDriver.waiting_edit_menu, filter_text('EDIT_CITY')]),
        Handler(handlers.edit_region, [EditDriver.waiting_edit_menu, filter_text('EDIT_REGION')]),
        Handler(handlers.details_top_up, [EditDriver.waiting_edit_menu, filter_text('TOP_UP')]),
        Handler(handlers.money_transfer, [TopUp.waiting_transfer, filter_text('MONEY_TRANSFERRED')]),
        Handler(handlers.open_menu, [TopUp.waiting_transfer, filter_text('OPEN_MENU')]),
        Handler(handlers.card_transfer, [TopUp.waiting_card, F.text]),
        Handler(handlers.amount_transfer, [TopUp.waiting_sum, F.text]),
        Handler(handlers.confirm_name, [EditDriver.waiting_name, F.text]),
        Handler(handlers.confirm_region, [EditDriver.waiting_region, F.text]),
        Handler(handlers.confirm_city, [EditDriver.waiting_city, F.text])
    ]

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

