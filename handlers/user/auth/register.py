from texts import TextManager, get_text_manager
from aiogram import types
from aiogram.fsm.context import FSMContext
from state.start import StartState
from state.register import RegisterState
from aiogram.types import ReplyKeyboardRemove
from handlers.common.helper import user_cabinet_menu
from bot import bot
from services.http_client import HttpUser
from services.google_maps import find_city, find_region
from services.visicom import search_settlement


async def save_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    await state.update_data(Phone=phone)

    await state.set_state(RegisterState.waiting_name)
    await message.answer(user_text_manager.asking.NAME, reply_markup=ReplyKeyboardRemove())


async def save_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(Name=name)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    await message.answer(text=user_text_manager.asking.REGION)
    await state.set_state(RegisterState.waiting_region)


async def save_region(message: types.Message, state: FSMContext):
    not_formatted_region = message.text
    region = await find_region(not_formatted_region)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    if region is None:
        await message.answer(user_text_manager.asking.REGION_NOT_FOUND)
        await message.answer(user_text_manager.asking.REGION)
        return

    await state.update_data(region=region)
    await message.answer(text=user_text_manager.asking.CITY)
    await state.set_state(RegisterState.waiting_city)


async def save_city(message: types.Message, state: FSMContext):
    not_formatted_city = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    region = data.get('region')
    city = search_settlement(not_formatted_city, region)
    if city == 'DUPLICATE':
        return message.answer(user_text_manager.asking.DUPLICATE_SETTLEMENT)

    if city is None:
        await message.answer(user_text_manager.asking.CITY_NOT_FOUND)
        await message.answer(user_text_manager.asking.CITY)
        return
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
        await state.set_data({**user_data, 'user_language': data.get('user_language')})
        await user_cabinet_menu(state, message=message)
        return

    return message.answer(user_text_manager.services.SERVER_ERROR)
