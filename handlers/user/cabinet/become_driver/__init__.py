from aiogram import Router, F
from handlers.user.cabinet.become_driver import handlers
from handlers.common.helper import Handler
from state.user import CreateDriver
from texts.keyboards import ALL_TRUE, OPEN_MENU


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.save_name, [CreateDriver.waiting_name, F.text]),
        Handler(handlers.save_region, [CreateDriver.waiting_region, F.text]),
        Handler(handlers.save_city, [CreateDriver.waiting_city, F.text]),
        Handler(handlers.save_car_name, [CreateDriver.waiting_car_name, F.text]),
        Handler(handlers.save_car_number, [CreateDriver.waiting_car_number, F.text]),
        Handler(handlers.save_car_number_of_seats, [CreateDriver.waiting_car_number_of_seats, F.text]),
        Handler(handlers.save_car_color, [CreateDriver.waiting_car_color, F.text]),
        Handler(handlers.save_passport_photo, [CreateDriver.waiting_passport_photo, F.photo]),
        Handler(handlers.save_license_photo, [CreateDriver.waiting_license_photo, F.photo]),
        Handler(handlers.save_insurance_photo, [CreateDriver.waiting_insurance_photo, F.photo]),
        Handler(handlers.save_car_photo, [CreateDriver.waiting_car_photo, F.photo]),
        Handler(handlers.confirm_request, [CreateDriver.waiting_accept, F.text == ALL_TRUE]),
        Handler(handlers.to_menu, [CreateDriver.waiting_accept, F.text == OPEN_MENU]),
    ]

    for message in message_list:
        router.message.register(message.handler, *message.filters)

    return router

