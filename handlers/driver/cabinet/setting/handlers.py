from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import json

from handlers.common.helper import driver_cabinet_menu
from services.http_client import HttpDriver
from state.driver import EditDriver, TopUp
from utils.template_engine import render_template
from aiogram.types import ReplyKeyboardRemove
from services.google_maps import find_city, find_region
from texts import TextManager, get_text_manager
from keyboards import KeyboardManager, get_kb_manager
from services.visicom import search_settlement


async def edit_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.NAME, reply_markup=ReplyKeyboardRemove())

    await state.set_state(EditDriver.waiting_name)


async def edit_city(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.CITY, reply_markup=ReplyKeyboardRemove())

    await state.set_state(EditDriver.waiting_city)


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

    response = await HttpDriver.update_driver(data={
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

    await state.set_state(EditDriver.waiting_region)


async def confirm_region(message: types.Message, state: FSMContext):
    not_formatted_region = message.text
    region = await find_region(not_formatted_region)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    chat_id = message.chat.id

    response = await HttpDriver.update_driver(data={
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

    response = await HttpDriver.update_driver(data={
        'chat_id': chat_id,
        'name': name,
    })

    if response.get('response_code') != 200:
        return message.answer(user_text_manager.services.SERVER_ERROR)
    await message.answer(user_text_manager.services.ASKING_EDIT_NAME)
    await state.update_data(name=name)

    await open_setting_menu(message, state)


async def open_setting_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    template = render_template("driver_info.js2", data=data, lang_code=data.get('user_language'))
    await message.answer(text=template, reply_markup=user_kb_manager.default.driver.edit_driver)

    await state.set_state(EditDriver.waiting_edit_menu)


async def open_menu(message: types.Message, state: FSMContext):
    await driver_cabinet_menu(state, message=message)


async def details_top_up(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(text=user_text_manager.asking.FOR_TOP_UP_BALANCE, reply_markup=user_kb_manager.default.driver.money_transferred, parse_mode="HTML")
    await state.set_state(TopUp.waiting_transfer)

async def money_transfer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    if user_text_manager.keyboards.OPEN_MENU == message.text:
        await open_menu(message, state)

    await message.answer(text=user_text_manager.asking.CARD_TRANSFER, reply_markup=ReplyKeyboardRemove())
    await state.set_state(TopUp.waiting_card)

async def card_transfer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    card = message.text
    await state.update_data(card_transfer=card)

    await message.answer(text=user_text_manager.asking.AMOUNT_TRANSFER)
    await state.set_state(TopUp.waiting_sum)

async def amount_transfer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    amount = message.text

    await HttpDriver.top_up_balance(data=
        {
            "cart_number": data.get('card_transfer'),
            "name": data.get('name'),
            "count": float(amount),
            "chat_id": message.chat.id
        }
    )

    await message.answer(text=user_text_manager.asking.TO_UP_END)
    await open_menu(message, state)