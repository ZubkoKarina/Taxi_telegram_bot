from typing import Any

from aiogram.fsm.context import FSMContext, StorageKey
from bot import bot, dp
from aiogram.fsm.state import StatesGroup, State

async def get_user_state(chat_id: int) -> FSMContext:
    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    return state

async def get_user_data(chat_id: int) -> dict:
    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    data = await state.get_data()

    return data

async def set_user_state(chat_id: int, new_state: State) -> None:
    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    await state.set_state(new_state)

async def get_element_from_user_data(chat_id: int, element_name: str) -> Any:
    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    data = await state.get_data()

    element = data.get(element_name, None)

    return element