import texts
from aiogram import types
from aiogram.fsm.context import FSMContext
from state.start import StartState
from state.register import RegisterState
from aiogram.types import ReplyKeyboardRemove
from keyboards.default.auth.register import phone_share_kb
from handlers.common.helper import user_cabinet_menu
from bot import bot
from services.http_client import HttpUser
from services.google_maps import find_city, find_region


async def save_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(Phone=phone)

    await state.set_state(RegisterState.waiting_name)
    await message.answer(texts.ASKING_NAME)


async def save_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(Name=name)
    data = await state.get_data()

    await message.answer(text=texts.ASKING_REGION)
    await state.set_state(RegisterState.waiting_region)


async def save_region(message: types.Message, state: FSMContext):
    not_formatted_region = message.text
    region = await find_region(not_formatted_region)
    await state.update_data(region=region)
    data = await state.get_data()

    await message.answer(text=texts.ASKING_CITY)
    await state.set_state(RegisterState.waiting_city)


async def save_city(message: types.Message, state: FSMContext):
    not_formatted_city = message.text
    data = await state.get_data()
    region = data.get('region')
    city = await find_city(not_formatted_city, region)
    await state.update_data(city=city)

    data = await state.get_data()

    response = await HttpUser.register_user(data={
        'name': data.get('Name'),
        'phone_number': data.get('Phone'),
        'city': data.get('city'),
        'region': data.get('region'),
        'chat_id': message.chat.id,
    })

    user_data = response.get('response_data').get('data')
    if response.get('response_code') == 200 and not user_data.get('is_banned'):
        await state.set_data(user_data)
        await user_cabinet_menu(state, message=message)
        return

    return message.answer(texts.SERVER_ERROR)
