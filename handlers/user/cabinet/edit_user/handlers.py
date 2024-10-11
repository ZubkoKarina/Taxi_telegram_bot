from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import json

from handlers.common.helper import user_cabinet_menu
from services.http_client import HttpUser
from state.user import EditUserInfo
from utils.template_engine import render_template
from aiogram.types import ReplyKeyboardRemove
from services.google_maps import find_city, find_region
from services.visicom import search_settlement
from keyboards import KeyboardManager, get_kb_manager
from texts import TextManager, get_text_manager


async def edit_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.NAME, reply_markup=ReplyKeyboardRemove())

    await state.set_state(EditUserInfo.waiting_name)


async def edit_city(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.CITY, reply_markup=ReplyKeyboardRemove())

    await state.set_state(EditUserInfo.waiting_city)


async def confirm_city(message: types.Message, state: FSMContext):
    not_formatted_city = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    region = data.get('region')
    city = search_settlement(not_formatted_city, region)
    if city == 'DUPLICATE':
        return message.answer(user_text_manager.asking.DUPLICATE_SETTLEMENT)

    chat_id = message.chat.id
    if city is None:
        await message.answer(user_text_manager.asking.CITY_NOT_FOUND)
        await message.answer(user_text_manager.asking.CITY)
        return
    response = await HttpUser.update_user(data={
        'chat_id': chat_id,
        'city': city,
    })

    if response.get('response_code') != 200:
        return message.answer(user_text_manager.services.SERVER_ERROR)
    await message.answer(user_text_manager.asking.EDIT_CITY)
    await state.update_data(city=city)
    print(await state.get_data())

    await open_setting_menu(message, state)


async def edit_region(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.REGION, reply_markup=ReplyKeyboardRemove())

    await state.set_state(EditUserInfo.waiting_region)


async def confirm_region(message: types.Message, state: FSMContext):
    not_formatted_region = message.text
    region = await find_region(not_formatted_region)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    chat_id = message.chat.id
    if region is None:
        await message.answer(user_text_manager.asking.REGION_NOT_FOUND)
        await message.answer(user_text_manager.asking.REGION)
        return

    response = await HttpUser.update_user(data={
        'chat_id': chat_id,
        'region': region,
    })

    if response.get('response_code') != 200:
        return message.answer(user_text_manager.services.SERVER_ERROR)
    await message.answer(user_text_manager.asking.EDIT_REGION)
    await state.update_data(region=region)
    print(await state.get_data())

    await open_setting_menu(message, state)


async def confirm_name(message: types.Message, state: FSMContext):
    name = message.text
    chat_id = message.chat.id
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpUser.update_user(data={
        'chat_id': chat_id,
        'name': name,
    })

    if response.get('response_code') != 200:
        return message.answer(user_text_manager.services.SERVER_ERROR)
    await message.answer(user_text_manager.asking.EDIT_NAME)
    await state.update_data(name=name)

    await open_setting_menu(message, state)


async def edit_language(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.CHOOSE_LANGUAGE, reply_markup=user_kb_manager.inline.choose_language.choose_language)
    await state.set_state(EditUserInfo.waiting_language)


async def init_language(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    if callback.data == 'uk_language':
        await state.update_data(user_language='uk')
    if callback.data == 'ru_language':
        await state.update_data(user_language='ru')
    if callback.data == 'en_language':
        await state.update_data(user_language='en')

    await open_setting_menu(callback.message, state)


async def open_setting_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    template = render_template("user_info.js2", data=data, lang_code=data.get('user_language'))
    await message.answer(text=template, reply_markup=user_kb_manager.default.users.edit_user)

    await state.set_state(EditUserInfo.waiting_edit_info)


async def open_menu(message: types.Message, state: FSMContext):
    await user_cabinet_menu(state, message=message)
