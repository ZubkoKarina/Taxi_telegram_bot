from pyexpat.errors import messages

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from handlers.common.helper import get_drivers, user_cabinet_menu, mass_notification_deletion, driver_cabinet_menu
from services.google_maps import geocode_place_by_name
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser, HttpDriver
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


async def order_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    if message.text == user_text_manager.keyboards.CANCEL_ORDER:
        await sure_cancel_order(message, state)
    if message.text == user_text_manager.keyboards.SEARCH_AGAIN:
        await create_order(order_data)
    if message.text == user_text_manager.keyboards.CHANGE_cost:
        await change_cost(message, state)
    if message.text == user_text_manager.keyboards.CHAT_WITH_DRIVER:
        await state.set_state(OrderTaxi.waiting_message_to_driver)
        await message.answer(user_text_manager.asking.SEND_MESSAGE_TO_DRIVER,
                             reply_markup=user_kb_manager.default.back)


async def ask_city(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(text=user_text_manager.asking.CITY, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderTaxi.waiting_new_city)


async def edit_city(message: types.Message, state: FSMContext):
    city = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

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

async def output_pre_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpOrder.get_user_order(data={'chat_id': message.chat.id})
    user_orders = response.get('response_data').get('data')
    last_user_order = user_orders[-1]

    template = render_template("order_passenger/pre_order.js2", data=last_user_order, lang_code=data.get('user_language'))
    message = await message.answer(template, reply_markup=user_kb_manager.default.users.pre_order)
    await state.update_data(msg_pre_order=message.message_id)

    await state.set_state(OrderTaxi.waiting_create_pre_order)

async def create_pre_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpOrder.get_user_order(data={'chat_id': message.chat.id})
    user_orders = response.get('response_data').get('data')
    last_user_order = user_orders[-1]

    await bot.delete_message(message.chat.id, data.get('msg_pre_order'))
    await create_order(last_user_order)

async def ask_open_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.CITY_ACCEPTED, reply_markup=ReplyKeyboardRemove())
    await message.answer(text=user_text_manager.asking.START_TAXI_ORDER,
                         reply_markup=user_kb_manager.inline.order.web_app)

    await state.set_state(OrderTaxi.waiting_order_data)


async def create_order(order_data: dict):
    chat_id = order_data.get("user_chat_id")

    response = await HttpUser.get_user_info({'chat_id': chat_id})
    is_banned = response.get('response_data').get('data').get('is_banned')
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
    form_data.add_field('comment', order_data.get('comment'))
    form_data.add_field('user_chat_id', chat_id)
    form_data.add_field('cost', float(order_data.get('cost')))

    response = await HttpOrder.create_order(data=form_data)
    if response.get('response_code') != 200:
        return await bot.send_message(chat_id=chat_id, text=user_text_manager.services.SERVER_ERROR)
    message = await bot.send_message(chat_id=chat_id, text=user_text_manager.asking.ORDER_DATA_RECEIVED,
                                     reply_markup=user_kb_manager.default.users.search_driver)
    await message.answer(str(order_data.get('variable')))

    order_id = response.get('response_data').get('data').get('id')
    await state.update_data(order_data={**order_data, 'id': order_id})
    await state.set_state(OrderTaxi.waiting_menu_order)

    if order_data.get('payMethod') == 'Карта':
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
    await state.update_data(payment_msg_id=msg.message_id)


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

    if order_data.get('payMethod') == 'Карта':
        await bot.delete_message(chat_id, data.get('payment_msg_id'))
        await state.update_data(payment_msg_id=None)

    template = render_template("order_passenger/order_info.js2", data=order_data, lang_code=data.get('user_language'))
    message = await bot.send_message(chat_id=chat_id, text=template, reply_markup=user_kb_manager.default.users.search_driver)
    msg_id_order_info = message.message_id

    await state.update_data(msg_id_order_info=msg_id_order_info)
    await search_drivers(message, state)


async def search_drivers(message: types.Message, state: FSMContext):
    passenger_data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(passenger_data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(passenger_data.get('user_language'))
    order_data = passenger_data.get('order_data')
    await state.update_data(MSG_WAIT_ACCEPT_ORDER=None)

    region = passenger_data.get('region')
    drivers = await get_drivers(region=region)

    print(f'ORDER DATA: {order_data}')
    if len(drivers) == 0:
        await message.answer(user_text_manager.asking.NOT_ACTIVE_DRIVER)
        return await open_menu(message, state)
    msg = await message.answer(text=user_text_manager.asking.SEARCH_DRIVER)
    msg_id = msg.message_id

    msg_for_driver_list = []
    drivers_id_list = []
    for drivers_by_rating in drivers:
        if len(drivers_by_rating) == 0:
            continue
        for driver in drivers_by_rating:
            geo_driver = driver.get('geo')
            from_geo = order_data.get('start_point').get('geo')
            distance_driver = haversine(from_geo, geo_driver)

            if distance_driver <= 10:
                driver_chat_id = driver.get('chat_id')

                template = render_template("order_driver/order_info.js2", data=order_data, lang_code=driver.get('user_language'))
                msg_for_driver = await bot.send_message(driver_chat_id, text=template,
                                                        reply_markup=user_kb_manager.inline.order.generation_notification_driver(
                                                            {'id': order_data.get('id')}))

                msg_for_driver_list.append(msg_for_driver.message_id)
                drivers_id_list.append(int(driver_chat_id))

                await bot.delete_message(message.chat.id, msg_id)
                search_info = {'msg_for_driver_list': msg_for_driver_list,
                               'drivers_id_list': drivers_id_list}

                await state.update_data(search_info=search_info)
        if len(drivers_id_list) != 0:
            is_driver_take_order = await waiting_accept_driver(message, state)
            if is_driver_take_order:
                return

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    await mass_notification_deletion(list_msg_id=msg_for_driver_list,
                                     list_chat_id=drivers_id_list)
    return await message.answer(user_text_manager.asking.NOT_SEARCH_DRIVER, reply_markup=user_kb_manager.default.users.no_search_driver)


async def waiting_accept_driver(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    if data['MSG_WAIT_ACCEPT_ORDER'] is None:
        msg = await message.answer(user_text_manager.asking.WAIT_ACCEPT_ORDER,
                                   reply_markup=user_kb_manager.default.users.search_driver)
        msg_id = msg.message_id
        await state.update_data(MSG_WAIT_ACCEPT_ORDER=msg_id)

    time_wait_driver = time.time()
    while True:
        response = await HttpOrder.get_order(data={'order_id': order_data.get('id')})
        if response.get('response_code') != 200:
            return False

        order_status = response.get('response_data').get('data').get('status')
        if order_status.get('id') != 1:
            await bot.delete_message(message.chat.id, msg_id)

            search_info = data.get('search_info')
            await mass_notification_deletion(list_msg_id=search_info.get('msg_for_driver_list'),
                                             list_chat_id=search_info.get('drivers_id_list'))

            order_data['driver_chat_id'] = response.get('response_data').get('data').get('driver_chat_id')
            order_data['time_order_accept'] = time.time()

            await state.update_data(order_data=order_data)
            await state.set_state(OrderTaxi.waiting_menu_order)
            return True

        elapsed_time = (time.time() - time_wait_driver)
        if elapsed_time > 20:
            return False
        await asyncio.sleep(5)


async def rate_driver(callback: types.CallbackQuery, state: FSMContext):
    callback_data = json.loads(callback.data)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    driver_rate = callback_data.get('rate')

    await HttpDriver.rete_driver(data={
        "chat_id": order_data.get('driver_chat_id'),
        "rate": int(driver_rate)
    })

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer(user_text_manager.asking.THANK_YOU)
    await open_menu(callback.message, state)


async def search_drivers_again(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    search_info = data.get('search_info')

    if search_info is not None:
        await mass_notification_deletion(list_msg_id=search_info.get('msg_for_driver_list'),
                                         list_chat_id=search_info.get('drivers_id_list'))
    await bot.delete_message(message.chat.id, data.get('msg_id_order_info'))
    await accept_order(order_data.get('id'))


async def change_cost(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    search_info = data.get('search_info')

    if search_info is not None:
        await mass_notification_deletion(list_msg_id=search_info.get('msg_for_driver_list'),
                                         list_chat_id=search_info.get('drivers_id_list'))

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    await message.answer(user_text_manager.asking.WAIT_cost, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderTaxi.waiting_new_cost)


async def take_cost(message: types.Message, state: FSMContext):
    cost = float(message.text)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    if float(order_data.get('cost')) > cost:
        return message.answer(user_text_manager.asking.COST_CHANGE_WARNING)
    order_data['cost'] = cost
    await bot.delete_message(message.chat.id, data.get('msg_id_order_info'))
    await message.answer(user_text_manager.asking.COST_UPDATED)

    if order_data.get('payMethod') == 'Карта':
        res = await refund_payment(order_data.get('id'))
        print(f"INFO: refund money -> {res.get('status')}")

    await create_order(order_data)


async def callback_message_to_driver(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await state.set_state(OrderTaxi.waiting_message_to_driver)
    await callback.message.answer(user_text_manager.asking.SEND_MESSAGE_TO_DRIVER, reply_markup=user_kb_manager.default.back)


async def send_message_to_driver(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    await bot.send_message(order_data.get('driver_chat_id'),
                           user_text_manager.asking.MESSAGE_FROM_PASSENGER,
                           f'\n{message.text}', reply_markup=user_kb_manager.inline.order_driver.reply_message_to_passenger)
    await message.answer(user_text_manager.asking.MESSAGE_SEND)


async def sure_cancel_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    if order_data.get('time_order_accept') is not None and order_data.get('payMethod') == 'Карта':
        elapsed_time = (time.time() - order_data.get('time_order_accept')) / 60
        if elapsed_time > 1:
            cost = order_data.get('cost')
            await message.answer(f'Кошти з замолення будуть повренені частково ({cost / 2} грн.)❗️')
    #
    await message.answer(user_text_manager.asking.ORDER_CANCEL_CONFIRMATION, reply_markup=user_kb_manager.default.yes_no)
    await state.set_state(OrderTaxi.waiting_cancel_order)


async def cancel_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    search_info = data.get('search_info')

    if search_info is not None:
        await mass_notification_deletion(list_msg_id=search_info.get('msg_for_driver_list'),
                                         list_chat_id=search_info.get('drivers_id_list'))
    if data.get('msg_id_order_info') is not None:
        await bot.delete_message(message.chat.id, data.get('msg_id_order_info'))
    if data.get('payment_msg_id') is not None:
        await bot.delete_message(message.chat.id, data.get('payment_msg_id'))
    if order_data.get('driver_chat_id') is not None:
        driver_id = order_data.get('driver_chat_id')
        driver_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=driver_id,
                                                                     user_id=driver_id, bot_id=bot.id))
        driver_msg = await bot.send_message(driver_id, user_text_manager.asking.ORDER_CANCELLED_BY_PASSENGER)

        cost = order_data.get('cost')
        if order_data.get('payMethod') == 'Карта':
            await bot.send_message(f'Вам надана компенсація в розмірі {cost / 2} грн.')
            await HttpDriver.insert_driver_balance(data={
                'chat_id': driver_id,
                'balance': cost / 2,
            })

        driver_state_data = await driver_state.get_data()
        processing_order_info_for_driver = driver_state_data.get('processing_order_info_for_driver')
        await bot.delete_message(driver_id, processing_order_info_for_driver)
        await driver_cabinet_menu(driver_state, message=driver_msg)

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    if order_data.get('payMethod') == 'Карта':
        res = await refund_payment(order_data.get('id'))
        print(f"INFO: refund money -> {res.get('status')}")

    await message.answer(user_text_manager.asking.ORDER_CANCELLED)

    await open_menu(message, state)


async def open_order_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.ORDER_MENU, reply_markup=user_kb_manager.default.users.order_menu)

    await state.set_state(OrderTaxi.waiting_menu_order)
