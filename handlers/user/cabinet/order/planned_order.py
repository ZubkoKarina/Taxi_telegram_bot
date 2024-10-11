from pyexpat.errors import messages

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

import re
from handlers.common.helper import get_drivers, user_cabinet_menu, driver_cabinet_menu, sort_drivers
from handlers.common import message_menager
from handlers.common.message_menager import delete_messages
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser, HttpDriver, HttpOther
from state.user import OrderTaxi, PlannedOrderTaxi
from services.liqpay import create_payment, refund_payment
from aiogram.types import ReplyKeyboardRemove
from bot import bot
from texts import TextManager, get_text_manager
from handlers.user.cabinet.common import open_menu
from bot import dp
import time
from keyboards import KeyboardManager, get_kb_manager
from utils.template_engine import render_template
from services.visicom import search_settlement
from datetime import datetime
import pytz

async def asking_date_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.DATE_PLANNED_ORDER, reply_markup=ReplyKeyboardRemove())
    await state.set_state(PlannedOrderTaxi.waiting_date_order)


async def save_date_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    timezone = pytz.timezone('Europe/Kyiv')
    date_order = message.text

    try:
        entered_date = datetime.strptime(date_order, "%d.%m.%Y").date()

        if entered_date >= datetime.now(timezone).date():
            await state.update_data(planned_order={'date': date_order, 'time': None})

            await message.answer(user_text_manager.asking.TIME_PLANNED_ORDER)
            await state.set_state(PlannedOrderTaxi.waiting_time_order)
        else:
            await message.answer(user_text_manager.validation.NOT_VALID_DATE)

    except ValueError:
        await message.answer(user_text_manager.validation.NOT_VALID_DATE)


import re
from datetime import datetime, time
import pytz

# Встановлюємо часовий пояс (+3) для коректної перевірки актуальності часу
TIMEZONE = pytz.timezone('Europe/Kiev')

async def save_time_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    time_order = message.text

    # Перевірка та корекція формату часу, наприклад, 16.00 -> 16:00
    time_order = re.sub(r'(\d{1,2})\.(\d{2})', r'\1:\2', time_order)

    try:
        # Перетворюємо строку часу у формат часу
        entered_time = datetime.strptime(time_order, "%H:%M").time()

        # Отримуємо поточну дату і час у заданому часовому поясі
        now = datetime.now(TIMEZONE)
        current_date = now.date()

        # Отримуємо заплановану дату з state (припускаємо, що її вже було збережено)
        planned_order = data.get('planned_order')
        planned_date_str = planned_order.get('date')  # дата повинна бути у форматі DD.MM.YYYY
        planned_date = datetime.strptime(planned_date_str, "%d.%m.%Y").date()

        # Якщо дата сьогоднішня, об'єднуємо її з введеним часом
        if planned_date == current_date:
            # Об'єднуємо дату і час
            entered_datetime_naive = datetime.combine(planned_date, entered_time)

            # Додаємо часовий пояс до entered_datetime
            entered_datetime = TIMEZONE.localize(entered_datetime_naive)

            # Перевіряємо, чи час не у минулому
            if entered_datetime < now:
                await message.answer(user_text_manager.validation.NOT_VALID_TIME)
                return
        elif planned_date < current_date:
            # Якщо запланована дата менша за поточну, то відхиляємо
            await message.answer(user_text_manager.validation.NOT_VALID_TIME)
            return

        # Якщо час коректний і дата актуальна, зберігаємо час
        planned_order['time'] = time_order
        await state.update_data(planned_order=planned_order)

        city = data.get("city")
        await message.answer(text=user_text_manager.asking.REQUEST_DRIVER_CONFIRMATION.format(city=city),
                             reply_markup=user_kb_manager.inline.order.web_app_accept_city)
        await state.set_state(PlannedOrderTaxi.waiting_accept_city)

    except ValueError:
        # Якщо формат часу некоректний
        await message.answer(user_text_manager.validation.NOT_VALID_TIME)




async def ask_city(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await callback.message.answer(text=user_text_manager.asking.CITY, reply_markup=ReplyKeyboardRemove())
    await callback.message.delete()
    await state.set_state(PlannedOrderTaxi.waiting_new_city)


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


async def start_planned_order(order_id):
    response = await HttpOrder.get_order(data={
        "order_id": order_id
    })
    order_data = response.get('response_data').get('data')
    chat_id: int = order_data.get('user_chat_id')

    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    data = await state.get_data()

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpDriver.get_driver_info(data={'chat_id': order_data.get('driver_chat_id')})
    driver_info = response.get('response_data').get('data')
    order_data['car_type_name'] = driver_info.get('car').get('car_type').get('name')

    template = render_template("order_passenger/order_info.js2", data=order_data, lang_code=data.get('user_language'))
    message = await bot.send_message(chat_id=chat_id, text=template)

    template = render_template("order_passenger/driver_info_for_planned_order.js2", data=driver_info, lang_code=data.get('user_language'))
    msg = await bot.send_message(chat_id=chat_id, text=template, reply_markup=user_kb_manager.inline.order.tracking_driver_app)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'driver_info')

    msg = await bot.send_message(chat_id=chat_id, text=user_text_manager.asking.PLANNED_ORDER_START, reply_markup=user_kb_manager.default.users.order_menu)
    await message_menager.add_to_message_list(msg, state, 'order_messages')

    await state.set_state(OrderTaxi.waiting_menu_order)
    await state.update_data(order_data=order_data, order_info_msg=message.message_id)