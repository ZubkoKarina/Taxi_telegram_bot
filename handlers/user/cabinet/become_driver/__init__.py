from aiogram import Router, F
from handlers.user.cabinet.become_driver import handlers
from handlers.common.helper import Handler
from state.user import CreateDriver
from texts import filter_text
from handlers import validation
from filters.valid_name import ValidFullNameFilter
from filters.valid_number import ValidNumberFilter


def prepare_router() -> Router:

    router = Router()
    message_list = [
        Handler(handlers.save_name, [CreateDriver.waiting_name, ValidFullNameFilter()]),
        Handler(handlers.save_region, [CreateDriver.waiting_region, F.text]),
        Handler(handlers.save_city, [CreateDriver.waiting_city, F.text]),
        Handler(handlers.save_car_name, [CreateDriver.waiting_car_name, F.text]),
        Handler(handlers.save_car_number, [CreateDriver.waiting_car_number, F.text]),
        Handler(handlers.save_car_number_of_seats, [CreateDriver.waiting_car_number_of_seats, ValidNumberFilter()]),
        Handler(handlers.save_car_color, [CreateDriver.waiting_car_color, F.text]),
        Handler(handlers.save_front_passport_photo, [CreateDriver.waiting_front_passport_photo, F.photo]),
        Handler(handlers.save_back_passport_photo, [CreateDriver.waiting_back_passport_photo, F.photo]),
        Handler(handlers.save_license_photo, [CreateDriver.waiting_license_photo, F.photo]),
        Handler(handlers.save_insurance_photo, [CreateDriver.waiting_insurance_photo, F.photo]),
        Handler(handlers.save_car_photo, [CreateDriver.waiting_car_photo, F.photo]),
        Handler(handlers.save_front_car_photo, [CreateDriver.waiting_front_car_photo, F.photo]),
        Handler(handlers.save_back_car_photo, [CreateDriver.waiting_back_car_photo, F.photo]),
        Handler(handlers.save_left_car_photo, [CreateDriver.waiting_left_car_photo, F.photo]),
        Handler(handlers.save_right_car_photo, [CreateDriver.waiting_right_car_photo, F.photo]),
        Handler(handlers.save_front_row_car_photo, [CreateDriver.waiting_front_row_car_photo, F.photo]),
        Handler(handlers.save_back_row_car_photo, [CreateDriver.waiting_back_row_car_photo, F.photo]),
        Handler(handlers.skip_comment, [CreateDriver.waiting_comment, filter_text('SKIP')]),
        Handler(handlers.save_comment, [CreateDriver.waiting_comment, F.text]),
        Handler(handlers.confirm_request, [CreateDriver.waiting_accept, filter_text('ALL_TRUE')]),
        Handler(handlers.to_menu, [CreateDriver.waiting_accept, filter_text('OPEN_MENU')]),
    ]

    validation_list = [
        Handler(validation.not_valid_text, [CreateDriver.waiting_name]),
        Handler(validation.not_valid_number, [CreateDriver.waiting_car_number_of_seats]),
    ]

    for message in [*message_list, *validation_list]:
        router.message.register(message.handler, *message.filters)

    return router

