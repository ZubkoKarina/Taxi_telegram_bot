import texts
from aiogram import types
from aiogram.fsm.context import FSMContext
from state.start import StartState
from state.register import RegisterState
from aiogram.types import ReplyKeyboardRemove
from keyboards.default.auth.register import phone_share_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.http_client import HttpUser, HttpDriver
from handlers.common.helper import driver_cabinet_menu, user_cabinet_menu


async def greeting(message: types.Message, state: FSMContext):
    await state.clear()
    response = await HttpDriver.get_driver_info({'chat_id': message.chat.id})
    user_data = response.get('response_data').get('data')
    if response.get('response_code') == 200 and not user_data.get('is_banned'):
        await state.set_data(user_data)
        await driver_cabinet_menu(state, message=message)
        return

    response = await HttpUser.get_user_info({'chat_id': message.chat.id})
    user_data = response.get('response_data').get('data')
    if response.get('response_code') == 200 and not user_data.get('is_banned'):
        await state.set_data(user_data)
        await user_cabinet_menu(state, message=message)
        return

    await message.answer(text=texts.GREETING, reply_markup=phone_share_kb)
    await state.set_state(RegisterState.waiting_phone)