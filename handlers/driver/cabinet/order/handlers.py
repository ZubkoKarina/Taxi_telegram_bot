from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from handlers.common.helper import mass_notification_deletion, driver_cabinet_menu
from services.liqpay import refund_payment, payment_completion
from services.google_maps import geocode_place_by_name, geocode_place_by_geo
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser
from state.user import OrderTaxi
from state.driver import OrderDriver
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from state.user import UserCabinetStates
from bot import bot
from texts import TextManager, get_text_manager
from utils.template_engine import render_template
from handlers.common.helper import driver_cabinet_menu
from bot import dp
import time
from keyboards import KeyboardManager, get_kb_manager


async def accept_order(callback: types.CallbackQuery, state: FSMContext):
    callback_data = json.loads(callback.data)
    order_id = callback_data.get('id')
    chat_id = callback.message.chat.id
    message = callback.message
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpOrder.accept_order(data={
        "driver_chat_id": chat_id,
        "order_id": order_id
    })
    if response.get('response_code') != 200:
        return await bot.send_message(chat_id=chat_id, text=user_text_manager.services.SERVER_ERROR)

    order_data = response.get('response_data').get('data')
    await state.update_data(order_data=order_data)

    await message.answer(text=user_text_manager.asking.TAKE_SUCCESSFUL, reply_markup=ReplyKeyboardRemove())

    template = render_template("order_driver/arrival_time.js2", data=order_data, lang_code=data.get('user_language'))
    await message.answer(text=template, reply_markup=user_kb_manager.inline.order_driver.arrival_time)


async def skip_order(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


async def take_arrival_time(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    callback_data = json.loads(callback.data)
    arrival_time = callback_data.get('arrival_time')
    order_data['arrival_time'] = arrival_time
    passenger_id = order_data.get('user_chat_id')
    msg_order_notification = []

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    template = render_template("order_passenger/driver_info.js2", data=data, lang_code=data.get('user_language'))
    msg_driver_info = await bot.send_message(chat_id=passenger_id, text=template, reply_markup=user_kb_manager.default.users.order_menu)
    msg_order_notification.append(callback.message.message_id)
    response = await HttpUser.get_user_info({'chat_id': passenger_id})
    user_data = response.get('response_data').get('data')

    template = render_template("order_driver/order_info_processing.js2",
                               data={**order_data, 'passenger_name': user_data.get('name')}, lang_code=data.get('user_language'))
    mgs = await callback.message.answer(text=template, reply_markup=user_kb_manager.inline.order_driver.menu)

    await state.update_data(msg_driver_info=msg_driver_info.message_id)
    await state.update_data(processing_order_info_for_driver=mgs.message_id)


async def driver_in_place(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    msg_order_notification = []

    msg = await bot.send_message(order_data.get('user_chat_id'), text=user_text_manager.asking.DRIVER_ARRIVED)
    msg_order_notification.append(msg.message_id)
    msg = await bot.send_message(order_data.get('user_chat_id'), text=user_text_manager.asking.EXTRA_WAITING_COST)
    msg_order_notification.append(msg.message_id)

    msg = await callback.message.answer(user_text_manager.asking.PASSENGER_NOTIFIED)
    msg_order_notification.append(msg.message_id)
    msg_order_notification.append(callback.message.message_id)

    await state.update_data(msg_order_notification=msg_order_notification, time_wait_passenger=time.time())
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        reply_markup=user_kb_manager.inline.order_driver.start)


async def sure_cancel_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await callback.message.answer(user_text_manager.asking.ORDER_CANCEL_CONFIRMATION, reply_markup=user_kb_manager.default.yes_no)
    await state.set_state(OrderDriver.waiting_cancel_order)


async def cancel_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    passenger_id = order_data.get('user_chat_id')
    driver_id = message.chat.id

    if data.get('msg_order_notification') is not None:
        await mass_notification_deletion([passenger_id, driver_id], data.get('msg_order_notification'))
    if data.get('msg_driver_info') is not None:
        await bot.delete_message(passenger_id, data.get('msg_driver_info'))

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    res = await refund_payment(order_data.get('id'))
    print(f"INFO: refund money -> {res.get('status')}")

    await bot.send_message(passenger_id, user_text_manager.asking.CANCELLED_BY_DRIVER)
    await message.answer(user_text_manager.asking.ORDER_CANCELLED)

    await driver_cabinet_menu(state, message=message)


async def start_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    passenger_id = order_data.get('user_chat_id')
    driver_id = callback.message.chat.id
    msg_order_notification = []
    await mass_notification_deletion([passenger_id, driver_id], data.get('msg_order_notification')[:3])

    elapsed_time = ((time.time() - data.get('time_wait_passenger')) / 60)
    if elapsed_time > 1:
        cost = float(order_data.get('cost'))
        cost = cost + (elapsed_time * 3)
        await HttpOrder.update_order(data={
            'order_id': order_data.get('id'),
            'cost': round(cost, 2)
        })

        await bot.send_message(passenger_id, f'Ціну збільшено на {(elapsed_time * 3)} за довге очікування ❗️')

    msg = await callback.message.answer(user_text_manager.asking.TRIP_STARTED)
    msg_order_notification.append(msg.message_id)
    msg_order_notification.append(callback.message.message_id)
    #
    msg = await bot.send_message(order_data.get('user_chat_id'), text=user_text_manager.asking.TRIP_STARTED,
                                 reply_markup=ReplyKeyboardRemove())
    msg_order_notification.append(msg.message_id)
    await state.update_data(msg_order_notification=msg_order_notification)
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id, reply_markup=user_kb_manager.inline.order_driver.end)


async def end_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    passenger_id = order_data.get('user_chat_id')
    driver_id = callback.message.chat.id

    await mass_notification_deletion([driver_id, passenger_id],
                                     data.get('msg_order_notification'))
    await bot.delete_message(passenger_id, data.get('msg_driver_info'))

    passenger_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=passenger_id,
                                                                    user_id=passenger_id, bot_id=bot.id))
    await passenger_state.set_state(OrderTaxi.waiting_rate_driver)

    await callback.message.answer(user_text_manager.asking.TRIP_ENDED)
    await bot.send_message(order_data.get('user_chat_id'), text=user_text_manager.asking.TRIP_ENDED)
    await bot.send_message(order_data.get('user_chat_id'), text=user_text_manager.asking.RATE_TRIP, reply_markup=user_kb_manager.inline.order.rate)
    await callback.message.answer(user_text_manager.asking.RATE_PASSENGER, reply_markup=user_kb_manager.inline.order.rate)

    if order_data.get('payMethod') == 'Карта':
        res = await payment_completion(order_data.get('id'))
        print(f"INFO: payment completion -> {res.get('status')}")

    await HttpOrder.complete_order({
        "user_chat_id": int(passenger_id),
        "driver_chat_id": int(driver_id),
        "order_id": int(order_data.get('id'))
    })

    await driver_cabinet_menu(state, message=callback.message)


async def rate_passenger(callback: types.CallbackQuery, state: FSMContext):
    callback_data = json.loads(callback.data)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    passenger_rate = callback_data.get('rate')
    await HttpUser.rete_user(data={
        "chat_id": order_data.get('user_chat_id'),
        "rate": int(passenger_rate)
    })

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


async def start_message_to_passenger(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await callback.message.answer(user_text_manager.asking.SEND_MESSAGE_TO_PASSENGER,
                                  reply_markup=user_kb_manager.default.back)

    await state.set_state(OrderDriver.waiting_message_to_passenger)


async def send_message_to_passenger(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    await bot.send_message(order_data.get('user_chat_id'), user_text_manager.asking.MESSAGE_FROM_DRIVER,
                           f'\n{message.text}', reply_markup=user_kb_manager.inline.order.reply_message_to_driver)
    await message.answer(user_text_manager.asking.MESSAGE_SEND)


async def open_order_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.ORDER_MENU, reply_markup=ReplyKeyboardRemove())

    await state.set_state(OrderTaxi.waiting_menu_order)


async def choice_type_navigation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    if callback.data == 'open_navigation_to':
        formatted_address = (f"{order_data['shipping_address']} {order_data['shipping_number']}, "
                             f"{order_data['shipping_city']}, {order_data['shipping_region']}")
        geocode_place = await geocode_place_by_name(formatted_address)

    elif callback.data == 'open_navigation_from':
        formatted_address = (f"{order_data['arrival_address']} {order_data['arrival_number']}, "
                             f"{order_data['arrival_city']}, {order_data['arrival_region']}")
        geocode_place = await geocode_place_by_name(formatted_address)

    choice_type_navigation_kb = user_kb_manager.inline.navigation.generation_buttons_navigation(location=geocode_place.get('location'))

    await callback.message.answer(user_text_manager.asking.NAVIGATION_METHOD_CHOICE, reply_markup=choice_type_navigation_kb)

# async def test(callback: types.CallbackQuery, state: FSMContext):
#     print(callback.data)