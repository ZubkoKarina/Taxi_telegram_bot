from pyexpat.errors import messages

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from handlers.common import message_menager
from services.http_client import HttpOrder, HttpUser, HttpDriver, HttpOther
from state.user import OrderTaxi
from services.liqpay import create_payment, refund_payment
from aiogram.types import ReplyKeyboardRemove
from bot import bot
from texts import TextManager, get_text_manager
from utils.template_engine import render_template
from bot import dp
from keyboards import KeyboardManager, get_kb_manager
import aiohttp
from .search_driver import search_drivers
from services.job_scheduler import scheduler
from datetime import datetime, timedelta

from ..common import open_menu


async def create_order(order_data: dict, state: FSMContext = None):
    chat_id = order_data.get("user_chat_id")

    response = await HttpUser.get_user_info({'chat_id': chat_id})
    is_banned = response.get('response_data').get('data').get('is_banned')

    if state is None:
        state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))

    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    if is_banned:
        return await bot.send_message(chat_id=chat_id, text=user_text_manager.services.USER_BANNED)

    print(f"INFO: order data -> {order_data}")

    form_data = aiohttp.FormData()
    form_data.add_field('start_point[address]', order_data.get('start_point').get('address'))
    form_data.add_field('start_point[geo_lat]', order_data.get('start_point').get('geo_lat'))
    form_data.add_field('start_point[geo_lng]', order_data.get('start_point').get('geo_lng'))

    form_data.add_field('end_point[address]', order_data.get('end_point').get('address'))
    form_data.add_field('end_point[geo_lat]', order_data.get('end_point').get('geo_lat'))
    form_data.add_field('end_point[geo_lng]', order_data.get('end_point').get('geo_lng'))

    for idx, point in enumerate(order_data.get('additional_point')):
        form_data.add_field(f'additional_points[{idx}][address]', point['address'])
        if point.get('geo') is not None:
            form_data.add_field(f'additional_points[{idx}][geo_lat]', point['geo'][0])
            form_data.add_field(f'additional_points[{idx}][geo_lng]', point['geo'][1])
        else:
            form_data.add_field(f'additional_points[{idx}][geo_lat]', point['geo_lat'])
            form_data.add_field(f'additional_points[{idx}][geo_lng]', point['geo_lng'])

    form_data.add_field('payment_method', order_data.get('payment_method'))
    form_data.add_field('car_type_id', int(order_data.get('car_type_id')))
    form_data.add_field('comment', order_data.get('comment'))
    form_data.add_field('user_chat_id', chat_id)
    form_data.add_field('cost', float(order_data.get('cost')))
    form_data.add_field('entrance', order_data.get('entrance'))

    if data.get('planned_order'):
        date = datetime.strptime(data.get('planned_order').get('date'), "%d.%m.%Y")
        time = datetime.strptime(data.get('planned_order').get('time'), "%H:%M")
        form_data.add_field('date', date.strftime("%d.%m.%Y"))
        form_data.add_field('time', time.strftime("%H:%M"))

    response = await HttpOrder.create_order(data=form_data)
    if response.get('response_code') != 200:
        return await bot.send_message(chat_id=chat_id, text=user_text_manager.services.SERVER_ERROR)

    message = await bot.send_message(chat_id=chat_id, text=user_text_manager.asking.ORDER_DATA_RECEIVED,
                                     reply_markup=user_kb_manager.default.users.search_driver)
    variable = order_data.get('variable')
    if variable is not None:
        await message.answer(str(variable))
        formatted_string = (
            f"x = ({variable['a']} * {variable['b']}) + "
            f"({variable['c']} * {variable['d']}) + "
            f"({variable['m']} * {variable['n']}) + "
            f"({variable['h']} * {variable['k']}) * {variable['p']}"
        )
        await message.answer(formatted_string, parse_mode=None)

    order_id = response.get('response_data').get('data').get('id')
    await state.update_data(order_data={**order_data, 'id': order_id, 'planned_order': data.get('planned_order', None)})
    await state.set_state(OrderTaxi.waiting_menu_order)

    if order_data.get('payMethod') == 'Онлайн_':
        await order_payment(state, message)
    else:
        await accept_order(order_id)


async def order_payment(state: FSMContext, message: types.Message):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    payment_url = await create_payment(order_data['cost'], order_data['id'])
    kb_for_paymemt = user_kb_manager.inline.order.generation_button_payment(payment_url)

    msg = await message.answer(user_text_manager.asking.PROCEED_TO_PAYMENT, reply_markup=kb_for_paymemt)
    await message_menager.add_to_message_list(message, state, 'order_messages')


async def accept_order(order_id: str):
    response = await HttpOrder.get_order(data={'order_id': order_id})

    chat_id = response.get('response_data').get('data').get('user_chat_id')
    order_data = response.get('response_data').get('data')

    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    if int(order_id) != int(order_data.get('id')):
        return

    if order_data.get('payMethod') == 'Онлайн_':
        await message_menager.delete_messages('order_messages', state)

    response = await HttpDriver.get_class_taxi()
    car_type_list = response.get('response_data').get('data')

    for car_type in car_type_list:
        if car_type.get('id') == order_data.get('car_type_id'):
            order_data['car_type_name'] = car_type.get('name')

    template = render_template("order_passenger/order_info.js2", data=order_data, lang_code=data.get('user_language'))
    message = await bot.send_message(chat_id=chat_id, text=template, reply_markup=user_kb_manager.default.users.search_driver)

    await state.update_data(order_data=order_data, order_info_msg=message.message_id)

    result_search_drivers = await search_drivers(message, state)
    if result_search_drivers and order_data.get('planned_order'):
        trip_time = order_data.get('planned_order').get('date') + " " + order_data.get('planned_order').get('time')
        trip_time = datetime.strptime(trip_time, "%d.%m.%Y %H:%M")

        trip_time -= timedelta(minutes=30)

        scheduler.add_job(create_notification_planned_order,
                          'date',
                          run_date=trip_time,
                          args=[order_data.get('id')],
                          misfire_grace_time=60)
        await open_menu(message, state)


async def create_notification_planned_order(order_id: int):
    response = await HttpOrder.get_order(data={'order_id': order_id})
    order_data = response.get('response_data').get('data')

    driver_chat_id = order_data.get('driver_chat_id')

    user_text_manager: TextManager = get_text_manager('uk')
    user_kb_manager: KeyboardManager = get_kb_manager('uk')
    template = render_template("order_driver/notification_planned_order.js2", data=order_data, lang_code='uk')

    await bot.send_message(int(driver_chat_id), text=template,
                           reply_markup=user_kb_manager.inline.order.generation_planned_order_driver(
                               {'id': order_data.get('id')}))

