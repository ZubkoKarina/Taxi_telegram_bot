from pyexpat.errors import messages

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from handlers.common.helper import get_drivers, user_cabinet_menu, driver_cabinet_menu, sort_drivers
from handlers.common import message_menager
from state import state_manager
from handlers.common.message_menager import delete_messages
from services.google_maps import geocode_place_by_name
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser, HttpDriver, HttpOther
from state.user import OrderTaxi
from services.liqpay import create_payment, refund_payment
from aiogram.types import ReplyKeyboardRemove
from bot import bot
from texts import TextManager, get_text_manager
from utils.template_engine import render_template
from handlers.user.cabinet.common import open_menu
from bot import dp
from services.visicom import get_place
import time
from keyboards import KeyboardManager, get_kb_manager
import aiohttp
from services.visicom import search_settlement


async def search_drivers(message: types.Message, state: FSMContext) -> bool:
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    region = data.get('region')
    drivers, count_driver, num_driver = None, None, 0

    async def drivers_record() -> bool:
        nonlocal drivers, count_driver, num_driver
        drivers = await get_drivers(region=region)
        if len(drivers) == 0:
            await message.answer(user_text_manager.asking.NOT_ACTIVE_DRIVER)
            await open_menu(message, state)
            return False
        result_sort = await sort_drivers(drivers)
        drivers = result_sort.get('sorted_drivers')
        count_driver = result_sort.get('count_driver')
        num_driver = 0

    msg = await message.answer(text=user_text_manager.asking.SEARCH_DRIVER)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'search_driver')

    driver_found = False
    await drivers_record()

    for drivers_by_priority in drivers:
        for drivers_by_rating in drivers_by_priority:
            if len(drivers_by_rating) == 0:
                continue
            for driver in drivers_by_rating:
                num_driver += 1
                if int(driver.get('car').get('car_type').get('id')) < int(order_data.get('car_type_id')):
                    continue
                geo_driver = driver.get('geo')
                driver_chat_id = int(driver.get('chat_id'))
                drivers_priority = driver.get('priority')
                driver_text_manager: TextManager = get_text_manager(driver.get('user_language'))
                from_geo = [order_data.get('start_point').get('geo_lat'), order_data.get('start_point').get('geo_lng')]

                if geo_driver is not None:
                    distance_driver = haversine(from_geo, geo_driver)
                else:
                    await bot.send_message(chat_id=driver_chat_id, text=driver_text_manager.asking.FAIL_GEO_DRIVER)
                    distance_driver = 1000

                if distance_driver <= 20:
                    driver_found = True
                    await state.update_data(drivers_priority=drivers_priority)

                    template = render_template("order_driver/order_info.js2",
                                               data={**order_data, 'time_order': data.get('time_order'), 'date_order': data.get('date_order')},
                                               lang_code=driver.get('user_language'))

                    msg = await bot.send_message(driver_chat_id, text=template,
                                                            reply_markup=user_kb_manager.inline.order.generation_notification_driver(
                                                                {'id': order_data.get('id')}))
                    await message_menager.add_to_message_list(msg, state, 'order_messages', 'for_driver')

                    await message_menager.delete_messages(state=state, name_message_list='order_messages', name_msg='search_driver')

            if driver_found:
                is_msg_send = await message_menager.find_message_in_list(state, 'order_messages', 'wait_accept_order')
                if not is_msg_send:
                    msg = await message.answer(user_text_manager.asking.WAIT_ACCEPT_ORDER,
                                               reply_markup=user_kb_manager.default.users.search_driver)
                    await message_menager.add_to_message_list(msg, state, 'order_messages', 'wait_accept_order')

                is_last_group = (num_driver == count_driver)
                if is_last_group:
                    drivers_priority = 'last'
                    await state.update_data(drivers_priority=drivers_priority)

                is_driver_take_order = await waiting_accept_driver(message, state)
                if is_driver_take_order == 'NEW_DRIVER_ON_LINE':
                    return await search_drivers(message, state)
                if is_driver_take_order:
                    response = await HttpOrder.get_order(data={'order_id': order_data.get('id')})
                    order_data['driver_chat_id'] = int(response.get('response_data').get('data').get('driver_chat_id'))

                if order_data.get('planned_order') and is_driver_take_order:
                    await message.answer(user_text_manager.asking.PLANNED_ORDER_SUCCESSFUL)
                    await delete_messages('order_messages', state)

                    await state.update_data(order_data=order_data)
                    return True
                elif is_driver_take_order:
                    order_data['driver_geo'] = geo_driver
                    order_data['time_order_accept'] = time.time()
                    await delete_messages('order_messages', state)

                    await state.update_data(order_data=order_data)
                    return True
                elif not is_driver_take_order and drivers_priority == 'last':
                    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
                    await message.answer(user_text_manager.asking.NOT_ACCEPT_DRIVER,
                                                reply_markup=user_kb_manager.default.users.no_search_driver)
                    return False

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    await message.answer(user_text_manager.asking.NOT_SEARCH_DRIVER, reply_markup=user_kb_manager.default.users.no_search_driver)
    return False


async def waiting_accept_driver(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    order_data = data.get('order_data')

    priority_time = {
        "1": 10,
        "2": 10,
        "last": 120,
    }

    drivers_priority = data.get('drivers_priority')
    waiting_time = priority_time.get(str(drivers_priority), 0)

    response = await HttpOther.get_status_fist_priority()
    fist_priority_status = response.get('response_data').get('data').get('is_active')
    if not fist_priority_status and drivers_priority == 1:
        waiting_time = 0
    print(waiting_time)

    time_wait_driver = time.time() + waiting_time
    while True:
        response = await HttpOrder.get_order(data={'order_id': order_data.get('id')})
        if response.get('response_code') != 200:
            return 'CANSEL'

        order_status = response.get('response_data').get('data').get('status')
        if order_status.get('id') != 1:

            await state.set_state(OrderTaxi.waiting_menu_order)
            return True

        elapsed_time = (time.time() - time_wait_driver)
        if elapsed_time > waiting_time:
            return False
        if drivers_priority == 'last':
            await check_for_new_driver(message, state)
        await asyncio.sleep(5)


async def check_for_new_driver(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    region = data.get('region')
    drivers = await get_drivers(region=region)
    for driver in drivers:
        driver_kb_manage: KeyboardManager = get_kb_manager(driver.get('user_language'))
        driver_chat_id: int = driver.get('chat_id')
        is_driver_notified = await message_menager.find_message_in_list(state, name_message_list='order_messages',
                                                                        chat_id=driver_chat_id)
        if is_driver_notified:
            continue
        geo_driver = await state_manager.get_element_from_user_data(driver_chat_id, 'geo')
        if geo_driver:
            from_geo = [order_data.get('start_point').get('geo_lat'), order_data.get('start_point').get('geo_lng')]
            distance_driver = haversine(from_geo, geo_driver)
            if distance_driver <= 20:
                template = render_template("order_driver/order_info.js2",
                                           data={**order_data, 'time_order': data.get('time_order'),
                                                 'date_order': data.get('date_order')},
                                           lang_code=driver.get('user_language'))

                msg = await bot.send_message(driver_chat_id, text=template,
                                             reply_markup=driver_kb_manage.inline.order.generation_notification_driver(
                                                 {'id': order_data.get('id')}))
                await message_menager.add_to_message_list(msg, state, 'order_messages', 'for_driver')