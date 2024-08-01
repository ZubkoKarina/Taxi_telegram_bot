from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from handlers.common.helper import get_drivers, user_cabinet_menu, mass_notification_deletion
from keyboards.inline.order import order_kb_inline, create_take_order_inline, create_kb_for_payment_inline
from keyboards.inline.order_for_driver import reply_message_to_passenger
from keyboards.default.users.order import order_menu_kb, order_search_driver_kb, order_no_search_driver_kb
from keyboards.default.go_back import back_kb
from keyboards.default.yes_no import yes_no_kb

from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser, HttpDriver
from state.user import OrderTaxi
from services.liqpay import create_payment, refund_payment
from aiogram.types import ReplyKeyboardRemove
from bot import bot
import texts
from texts.keyboards import CANCEL_ORDER, CHANGE_PRICE, SEARCH_AGAIN, CHAT_WITH_DRIVER, YES, NO
from utils.template_engine import render_template
from texts.keyboards import OPEN_MENU
from handlers.user.cabinet.common import open_menu
from bot import dp
import time


async def order_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    if message.text == CANCEL_ORDER:
        await sure_cancel_order(message, state)
    if message.text == SEARCH_AGAIN:
        await create_order(order_data)
    if message.text == CHANGE_PRICE:
        await change_price(message, state)
    if message.text == CHAT_WITH_DRIVER:
        await state.set_state(OrderTaxi.waiting_message_to_driver)
        await message.answer('Надішліть мені повідомлення і я його перешлю водія.',
                             reply_markup=back_kb)


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

    await message.answer('Місто прийнято ✅', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Для початку оформлення таксі нажміть кнопку нище 👇',
                         reply_markup=order_kb_inline)

    await state.set_state(OrderTaxi.waiting_order_data)


async def create_order(order_data: dict):
    chat_id = order_data.get("chat_id")
    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))

    list_from_dict = order_data.get('addressFrom').split(",")
    list_to_dict = order_data.get('addressTo').split(",")

    print(f"INFO: order data -> {order_data}")
    if order_data.get('otherSetting') is not None:
        is_other_setting = any(value is True for value in order_data.get('otherSetting').values())
        order_data['isOtherSetting'] = is_other_setting

    order_data["from_dict"] = {
        "street": list_from_dict[0],
        "region": list_from_dict[3],
        "city": list_from_dict[2],
        "house": list_from_dict[1],
    }
    order_data["to_dict"] = {
        "street": list_to_dict[0],
        "region": list_to_dict[3],
        "city": list_to_dict[2],
        "house": list_to_dict[1],
    }

    response = await HttpOrder.create_order(data={
        "shipping_address": list_from_dict[0],
        "shipping_region": list_from_dict[3],
        "shipping_city": list_from_dict[2],
        "shipping_number": list_from_dict[1],
        "arrival_address": list_to_dict[0],
        "arrival_region": list_to_dict[3],
        "arrival_city": list_to_dict[2],
        "arrival_number": list_to_dict[1],
        "payment_method": order_data.get('payMethod'),
        "comment": "some",
        "user_chat_id": chat_id,
        "cost": (float(order_data.get('price'))),
    })
    if response.get('response_code') != 200:
        return await bot.send_message(chat_id=chat_id, text=texts.SERVER_ERROR)
    message = await bot.send_message(chat_id=chat_id, text='Дані отримано, замолення формується...',
                                     reply_markup=order_search_driver_kb)

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
    order_data = data.get('order_data')

    payment_url = await create_payment(order_data['price'], order_data['id'])
    kb_for_paymemt = create_kb_for_payment_inline(payment_url)

    msg = await message.answer('Натисніть кнопку нижче для оплати 👇', reply_markup=kb_for_paymemt)
    await state.update_data(payment_msg_id=msg.message_id)


async def accept_order(order_id: str):
    response = await HttpOrder.get_order(data={'order_id': order_id})
    print(response.get('response_data').get('data'))
    chat_id = response.get('response_data').get('data').get('user_chat_id')

    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    data = await state.get_data()
    order_data = data.get('order_data')
    if int(order_id) != int(order_data.get('id')):
        return

    if order_data.get('payMethod') == 'Карта':
        await bot.delete_message(chat_id, data.get('payment_msg_id'))
        await state.update_data(payment_msg_id=None)

    template = render_template("order_info.js2", data=order_data)
    message = await bot.send_message(chat_id=chat_id, text=template, reply_markup=order_search_driver_kb)
    msg_id_order_info = message.message_id

    await state.update_data(msg_id_order_info=msg_id_order_info)
    await search_drivers(message, state)


async def search_drivers(message: types.Message, state: FSMContext):
    passenger_data = await state.get_data()
    order_data = passenger_data.get('order_data')

    region = order_data.get('from_dict').get('region')
    drivers = await get_drivers(region=region)

    print(f'ORDER DATA: {order_data}')
    if len(drivers) == 0:
        await message.answer(texts.ASKING_NOT_ACTIVE_DRIVER)
        return await open_menu(message, state)
    msg = await message.answer(text=texts.ASKING_SEARCH_DRIVER)
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

            template = render_template("order_info_for_driver.js2", data=order_data)
            msg_for_driver = await bot.send_message(driver_chat_id, text=template,
                                                    reply_markup=create_take_order_inline({'id': order_data.get('id')}))

            msg_for_driver_list.append(msg_for_driver.message_id)
            drivers_id_list.append(int(driver_chat_id))

            await bot.delete_message(message.chat.id, msg_id)
            search_info = {'msg_for_driver_list': msg_for_driver_list,
                           'drivers_id_list': drivers_id_list}

            await state.update_data(search_info=search_info)
            return await waiting_accept_driver(message, state)

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    return await message.answer(texts.ASKING_NOT_SEARCH_DRIVER, reply_markup=order_no_search_driver_kb)


async def waiting_accept_driver(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    msg = await message.answer(texts.ASKING_WAIT_ACCEPT_ORDER, reply_markup=order_search_driver_kb)
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

    await message.answer(texts.ASKING_NOT_ACCEPT_DRIVER, reply_markup=order_no_search_driver_kb)
    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})


async def rate_driver(callback: types.CallbackQuery, state: FSMContext):
    callback_data = json.loads(callback.data)
    data = await state.get_data()
    order_data = data.get('order_data')

    driver_rate = callback_data.get('rate')

    await HttpDriver.rete_driver(data={
        "chat_id": order_data.get('driver_chat_id'),
        "rate": int(driver_rate)
    })

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await callback.message.answer('Дякуємо!')
    await open_menu(callback.message, state)


async def search_drivers_again(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    search_info = data.get('search_info')

    if search_info is not None:
        await mass_notification_deletion(list_msg_id=search_info.get('msg_for_driver_list'),
                                         list_chat_id=search_info.get('drivers_id_list'))
    await bot.delete_message(message.chat.id, data.get('msg_id_order_info'))
    await accept_order(order_data.get('id'))


async def change_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    search_info = data.get('search_info')

    if search_info is not None:
        await mass_notification_deletion(list_msg_id=search_info.get('msg_for_driver_list'),
                                         list_chat_id=search_info.get('drivers_id_list'))

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    await message.answer(texts.ASKING_WAIT_PRICE)
    await state.set_state(OrderTaxi.waiting_new_price)


async def take_price(message: types.Message, state: FSMContext):
    price = float(message.text)
    data = await state.get_data()
    order_data = data.get('order_data')
    if float(order_data.get('price')) > price:
        return message.answer('Нова ціна не може бути нижчою за попередню ❗️')
    order_data['price'] = price
    await bot.delete_message(message.chat.id, data.get('msg_id_order_info'))
    await message.answer('Ціну зміненно ✅')

    if order_data.get('payMethod') == 'Карта':
        res = await refund_payment(order_data.get('id'))
        print(f"INFO: refund money -> {res.get('status')}")

    await create_order(order_data)


async def callback_message_to_driver(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(OrderTaxi.waiting_message_to_driver)
    await callback.message.answer('Надішліть мені повідомлення і я його перешлю водія.', reply_markup=back_kb)


async def send_message_to_driver(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    await bot.send_message(order_data.get('driver_chat_id'),
                           f'Повідомлення від пасажира 💬'
                           f'\n{message.text}', reply_markup=reply_message_to_passenger)
    await message.answer('Повідомлення вітправлено ✅')


async def sure_cancel_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    if order_data.get('time_order_accept') is not None and order_data.get('payMethod') == 'Карта':
        elapsed_time = (time.time() - order_data.get('time_order_accept')) / 60
        if elapsed_time > 1:
            price = order_data.get('price')
            await message.answer(f'Кошти з замолення будуть повренені частково ({price / 2} грн.)❗️')

    await message.answer('Ви впевнені що бажаєте скасуваити замолення', reply_markup=yes_no_kb)
    await state.set_state(OrderTaxi.waiting_cancel_order)


async def cancel_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
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
        await bot.send_message('Пасажир скасував замолення 🚫')

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

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    if order_data.get('payMethod') == 'Карта':
        res = await refund_payment(order_data.get('id'))
        print(f"INFO: refund money -> {res.get('status')}")

    await message.answer('Замолення скасовано 🚫')

    await open_menu(message, state)


async def open_order_menu(message: types.Message, state: FSMContext):
    await message.answer('Меню замолення', reply_markup=order_menu_kb)

    await state.set_state(OrderTaxi.waiting_menu_order)
