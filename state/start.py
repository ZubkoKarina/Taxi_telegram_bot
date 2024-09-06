from aiogram.fsm.state import StatesGroup, State


class StartState(StatesGroup):
    waiting_greeting = State()
    waiting_language = State()
