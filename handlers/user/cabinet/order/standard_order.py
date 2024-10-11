from pyexpat.errors import messages

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from handlers.common.helper import get_drivers, user_cabinet_menu, driver_cabinet_menu, sort_drivers
from handlers.common import message_menager
from handlers.common.message_menager import delete_messages
from services.google_maps import geocode_place_by_name
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser, HttpDriver, HttpOther
from state.user import OrderTaxi
from services.liqpay import create_payment, refund_payment
from aiogram.types import ReplyKeyboardRemove
from bot import bot
from texts import TextManager, get_text_manager
from keyboards import KeyboardManager, get_kb_manager
import aiohttp
from services.visicom import search_settlement


async def ask_confirm_city(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    city = data.get("city")
    await message.answer(text=user_text_manager.asking.REQUEST_DRIVER_CONFIRMATION.format(city=city),
                         reply_markup=user_kb_manager.inline.order.web_app_accept_city)
    # await state.set_state(OrderTaxi.waiting_accept_city)
    await state.update_data(planned_order=None)


async def ask_city(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await callback.message.answer(text=user_text_manager.asking.CITY, reply_markup=ReplyKeyboardRemove())
    await callback.message.delete()
    await state.set_state(OrderTaxi.waiting_new_city)


async def edit_city(message: types.Message, state: FSMContext):
    not_formatted_city = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    region = data.get('region')

    city = search_settlement(not_formatted_city, region)
    if city == 'DUPLICATE':
        return message.answer(user_text_manager.asking.DUPLICATE_SETTLEMENT)

    if city is None:
        await message.answer(user_text_manager.asking.CITY_NOT_FOUND)
        await message.answer(user_text_manager.asking.CITY)
        return
    response = await HttpUser.update_user(data={
        'chat_id': message.chat.id,
        'city': city,
    })
    if response.get('response_code') != 200:
        return message.answer(user_text_manager.services.SERVER_ERROR)
    await state.update_data(city=city)

    await ask_open_order(message, state)

async def ask_open_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.CITY_ACCEPTED, reply_markup=ReplyKeyboardRemove())
    await message.answer(text=user_text_manager.asking.START_TAXI_ORDER,
                         reply_markup=user_kb_manager.inline.order.web_app)

    await state.set_state(OrderTaxi.waiting_order_data)