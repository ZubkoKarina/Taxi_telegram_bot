from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from state.user import CreateDriver
from handlers.common.helper import user_cabinet_menu
import json
from texts import TextManager, get_text_manager
from handlers.common.ending_route import ask_raw_message


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    if bt_text == user_text_manager.keyboards.REPORT_ISSUE:
        pass
    elif bt_text == user_text_manager.keyboards.BECOME_PARTNER:
        await become_driver(message, state)
    else:
        await ask_raw_message(message, state)


async def open_menu(message: types.Message, state: FSMContext):
    await user_cabinet_menu(state, message=message)


async def become_driver(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.BECOME_PARTNER
                         )
    await message.answer(user_text_manager.asking.SEND_FULL_NAME, reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateDriver.waiting_name)