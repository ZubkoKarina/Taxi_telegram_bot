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


async def order_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    if message.text == user_text_manager.keyboards.CANCEL_ORDER:
        await sure_cancel_order(message, state)
    if message.text == user_text_manager.keyboards.SEARCH_AGAIN:
        await create_order(order_data)
    if message.text == user_text_manager.keyboards.CHANGE_PRICE:
        await change_price(message, state)
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


async def ask_open_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.CITY_ACCEPTED, reply_markup=ReplyKeyboardRemove())
    await message.answer(text=user_text_manager.asking.START_TAXI_ORDER,
                         reply_markup=user_kb_manager.inline.order.web_app)

    await state.set_state(OrderTaxi.waiting_order_data)


async def create_order(order_data: dict):
    chat_id = order_data.get("chat_id")
    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    id_from = order_data.get('addressFrom')
    id_to = order_data.get('addressTo')

    print(f"INFO: order data -> {order_data}")

    from_dict = get_place(place_id=id_from, categories='adr_address')
    to_dict = get_place(place_id=id_to, categories='adr_address')
    to_dict = to_dict.get('address')
    from_dict = from_dict.get('address')

    order_data["from_dict"] = from_dict
    order_data["to_dict"] = to_dict

    response = await HttpOrder.create_order(data={
        "shipping_address": from_dict['street'],
        "shipping_region": data.get('region'),
        "shipping_city": from_dict['city'],
        "shipping_number": from_dict['house'],
        "arrival_address": to_dict['street'],
        "arrival_region": data.get('region'),
        "arrival_city": to_dict['city'],
        "arrival_number": to_dict['house'],
        "payment_method": order_data.get('payMethod'),
        "comment": order_data.get('comment'),
        "user_chat_id": chat_id,
        "cost": (float(order_data.get('price'))),
    })
    if response.get('response_code') != 200:
        return await bot.send_message(chat_id=chat_id, text=user_text_manager.services.SERVER_ERROR)
    message = await bot.send_message(chat_id=chat_id, text=user_text_manager.asking.ORDER_DATA_RECEIVED,
                                     reply_markup=user_kb_manager.default.users.search_driver)

    order_id = response.get('response_data').get('data').get('id')
    order_data['id'] = order_id
    await state.update_data(order_data=order_data)
    await state.set_state(OrderTaxi.waiting_menu_order)

    if order_data.get('payMethod') == 'Карта':
        await order_payment(state, message)
    else:
        await accept_order(order_data.get('id'))


async def order_payment(state: FSMContext, message: types.Message):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    payment_url = await create_payment(order_data['price'], order_data['id'])
    kb_for_paymemt = user_kb_manager.inline.order.generation_button_payment(payment_url)

    msg = await message.answer(user_text_manager.asking.PROCEED_TO_PAYMENT, reply_markup=kb_for_paymemt)
    await state.update_data(payment_msg_id=msg.message_id)


async def accept_order(order_id: str):
    response = await HttpOrder.get_order(data={'order_id': order_id})
    print(response.get('response_data').get('data'))
    chat_id = response.get('response_data').get('data').get('user_chat_id')

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

    region = passenger_data.get('region')
    drivers = await get_drivers(region=region)

    print(f'ORDER DATA: {order_data}')
    if len(drivers) == 0:
        await message.answer(user_text_manager.asking.NOT_ACTIVE_DRIVER)
        return await open_menu(message, state)
    msg = await message.answer(text=user_text_manager.asking.SEARCH_DRIVER)
    msg_id = msg.message_id

    for driver in drivers:
        msg_for_driver_list = []
        drivers_id_list = []

        geo_driver = driver.get('geo')
        from_geo = order_data.get('fromCoordinates')
        print(f'{geo_driver} and {from_geo}')
        distance_driver = haversine(from_geo, geo_driver)

        if distance_driver <= 10:
            driver_chat_id = driver.get('chat_id')

            template = render_template("order_driver/order_info.js2", data=order_data, lang_code=driver.get('lang_code'))
            msg_for_driver = await bot.send_message(driver_chat_id, text=template,
                                                    reply_markup=user_kb_manager.inline.order.generation_notification_driver({'id': order_data.get('id')}))

            msg_for_driver_list.append(msg_for_driver.message_id)
            drivers_id_list.append(int(driver_chat_id))

            await bot.delete_message(message.chat.id, msg_id)
            search_info = {'msg_for_driver_list': msg_for_driver_list,
                           'drivers_id_list': drivers_id_list}

            await state.update_data(search_info=search_info)
            return await waiting_accept_driver(message, state)

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    return await message.answer(user_text_manager.asking.NOT_SEARCH_DRIVER, reply_markup=user_kb_manager.default.users.no_search_driver)


async def waiting_accept_driver(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    msg = await message.answer(user_text_manager.asking.WAIT_ACCEPT_ORDER, reply_markup=user_kb_manager.default.users.search_driver)
    msg_id = msg.message_id

    time_wait_driver = time.time()
    while True:
        response = await HttpOrder.get_order(data={'order_id': order_data.get('id')})
        if response.get('response_code') != 200:
            return

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
            return

        elapsed_time = (time.time() - time_wait_driver) / 60
        if elapsed_time > 5:
            break
        await asyncio.sleep(5)

    await message.answer(user_text_manager.asking.NOT_ACCEPT_DRIVER, reply_markup=user_kb_manager.default.users.no_search_driver)
    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})


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


async def change_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    search_info = data.get('search_info')

    if search_info is not None:
        await mass_notification_deletion(list_msg_id=search_info.get('msg_for_driver_list'),
                                         list_chat_id=search_info.get('drivers_id_list'))

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    await message.answer(user_text_manager.asking.WAIT_PRICE, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderTaxi.waiting_new_price)


async def take_price(message: types.Message, state: FSMContext):
    price = float(message.text)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    if float(order_data.get('price')) > price:
        return message.answer(user_text_manager.asking.PRICE_CHANGE_WARNING)
    order_data['price'] = price
    await bot.delete_message(message.chat.id, data.get('msg_id_order_info'))
    await message.answer(user_text_manager.asking.PRICE_UPDATED)

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
            price = order_data.get('price')
            await message.answer(f'Кошти з замолення будуть повренені частково ({price / 2} грн.)❗️')
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

        price = order_data.get('price')
        if order_data.get('payMethod') == 'Карта':
            await bot.send_message(f'Вам надана компенсація в розмірі {price / 2} грн.')
            await HttpDriver.insert_driver_balance(data={
                'chat_id': driver_id,
                'balance': price / 2,
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
