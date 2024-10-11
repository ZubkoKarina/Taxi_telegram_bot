from aiogram.fsm.state import StatesGroup, State


class DriverCabinetStates(StatesGroup):
    waiting_menu = State()
    waiting_geo = State()
    waiting_history_order = State()


class OrderDriver(StatesGroup):
    waiting_order = State()
    waiting_message_to_passenger = State()
    waiting_cancel_order = State()

    waiting_sos_comment = State()
    waiting_menu_order = State()

    waiting_replace_cost = State()
    waiting_accept_replace_cost = State()


class EditDriver(StatesGroup):
    waiting_edit_menu = State()
    waiting_name = State()
    waiting_region = State()
    waiting_city = State()

class TopUp(StatesGroup):
    waiting_transfer = State()
    waiting_card = State()
    waiting_sum = State()