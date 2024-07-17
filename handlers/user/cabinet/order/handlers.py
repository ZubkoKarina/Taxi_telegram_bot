from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from handlers.common.helper import get_drivers, user_cabinet_menu
from keyboards.inline.order import order_kb_inline
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser
from state.user import OrderTaxi
from aiogram.types import ReplyKeyboardRemove
from bot import bot
import texts
from utils.template_engine import render_template
from texts.keyboards import OPEN_MENU
from handlers.user.cabinet.common import open_menu
from bot import dp


async def ask_city(message: types.Message, state: FSMContext):
    await message.answer(text=texts.ASKING_CITY, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderTaxi.waiting_new_city)


async def edit_city(message: types.Message, state: FSMContext):
    city = message.text

    response = await HttpUser.update_user(data={
        'chat_id': message.chat.id,
        'city': city,
    })
    if response.get('response_code') != 200:
        return message.answer(texts.SERVER_ERROR)
    await state.update_data(city=city)

    await ask_open_order(message, state)


async def ask_open_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    city = data.get('city')
    await message.answer('Місто прийнято✅', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Для початку оформлення таксі нажміть кнопку нище 👇',
                         reply_markup=order_kb_inline)

    await state.set_state(OrderTaxi.waiting_order_data)


async def accept_order_data(order_data: dict):
    chat_id = order_data.get("chat_id")
    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))

    cleaned_string = order_data.get('price').replace(",", "")
    price_float = float(cleaned_string)

    await state.update_data(order_data=order_data)
    response = await HttpOrder.create_order(data={
        "shipping_address": order_data.get('addressFrom'),
        "arrival_address": order_data.get('addressTo'),
        "payment_method": order_data.get('payMethod'),
        "comment": 'nothing',
        "user_chat_id": chat_id,
        "cost": price_float,
    })
    if response.get('response_code') != 200:
        return await bot.send_message(chat_id=chat_id, text=texts.SERVER_ERROR)

    template = render_template("order_info.js2", data=order_data)
    message = await bot.send_message(chat_id=chat_id, text=template)
    await search_drivers(message, state)


async def search_drivers(message: types.Message, state: FSMContext):
    drivers = await get_drivers()
    passenger_data = await state.get_data()
    order_data = passenger_data.get('order_data')
    print(f'ORDER DATA: {order_data}')
    if len(drivers) == 0:
        await message.answer(texts.ASKING_NOT_ACTIVE_DRIVER)
        return await open_menu(message, state)
    msg = await message.answer(text=texts.ASKING_SEARCH_DRIVER)
    msg_id = msg.message_id
    for _ in range(5):
        for driver in drivers:
            geo_driver = driver.get('geo')
            from_geo = order_data.get('fromCoordinates')
            print(f'{geo_driver} and {from_geo}')
            distance_driver = haversine(from_geo, geo_driver)
            if distance_driver <= 10:
                driver_chat_id = driver.get('chat_id')
                template = render_template("order_info_for_driver.js2", data=order_data)

                await bot.send_message(driver_chat_id, text=template)

                await bot.delete_message(message.chat.id, msg_id)
                return await message.answer(texts.ASKING_WAIT_ACCEPT_ORDER)
        await asyncio.sleep(10)

    await bot.delete_message(message.chat.id, msg_id)
    await message.answer(texts.ASKING_NOT_SEARCH_DRIVER)

    await open_menu(message, state)
