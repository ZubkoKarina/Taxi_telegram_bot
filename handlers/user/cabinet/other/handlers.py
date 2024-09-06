from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from state.user import CreateDriver
from handlers.common.helper import user_cabinet_menu
import json
from texts import TextManager, get_text_manager


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    if bt_text == user_text_manager.keyboards.REPORT_ISSUE:
        pass
    elif bt_text == user_text_manager.keyboards.BECOME_PARTNER:
        await message.answer(user_text_manager.asking.BECOME_PARTNER
                             )
        await message.answer(user_text_manager.asking.SEND_FULL_NAME, reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateDriver.waiting_name)


async def open_menu(message: types.Message, state: FSMContext):
    await user_cabinet_menu(state, message=message)
