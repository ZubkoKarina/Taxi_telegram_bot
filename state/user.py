from aiogram.fsm.state import StatesGroup, State


class UserCabinetStates(StatesGroup):
    waiting_menu = State()
    waiting_history_order = State()


class EditUserInfo(StatesGroup):
    waiting_edit_info = State()
    waiting_name = State()
    waiting_region = State()
    waiting_city = State()


class OtherFun(StatesGroup):
    waiting_other_fun = State()


class OrderTaxi(StatesGroup):
    waiting_accept_city = State()
    waiting_new_city = State()

    waiting_order_data = State()
    waiting_menu_order = State()

    waiting_new_price = State()
    waiting_rate_driver = State()


class CreateDriver(StatesGroup):
    waiting_name = State()

    waiting_region = State()
    waiting_city = State()

    waiting_car_name = State()
    waiting_car_number = State()
    waiting_car_number_of_seats = State()
    waiting_car_color = State()

    waiting_passport_photo = State()
    waiting_license_photo = State()
    waiting_insurance_photo = State()
    waiting_car_photo = State()

    waiting_accept = State()

