from aiogram.fsm.state import StatesGroup, State


class DriverCabinetStates(StatesGroup):
    waiting_menu = State()
    waiting_geo = State()


class OrderTaxi(StatesGroup):
    waiting_order = State()
