from aiogram.fsm.state import StatesGroup, State


class UserCabinetStates(StatesGroup):
    waiting_menu = State()
    waiting_history_order = State()


class EditUserInfo(StatesGroup):
    waiting_edit_info = State()
    waiting_name = State()
    waiting_city = State()


class OtherFun(StatesGroup):
    waiting_other_fun = State()


class OrderTaxi(StatesGroup):
    waiting_accept_city = State()
    waiting_new_city = State()
    waiting_order_data = State()
