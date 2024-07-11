from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from handlers.common.helper import user_cabinet_menu
import json

from texts.keyboards import REPORT_ISSUE, BECOME_PARTNER
import texts


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text
    data = await state.get_data()

    if bt_text == REPORT_ISSUE:
        pass
    elif bt_text == BECOME_PARTNER:
        pass

async def open_menu(message: types.Message, state: FSMContext):
    await user_cabinet_menu(state, message=message)
