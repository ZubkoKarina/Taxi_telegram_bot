from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from keyboards.default.users.order import order_menu_kb
from keyboards.inline.order_for_driver import driver_order_menu, driver_order_start, driver_order_end, \
    order_arrival_time
from keyboards.default.go_back import back_kb
from keyboards.inline.order import rate, reply_message_to_driver
from keyboards.default.yes_no import yes_no_kb

from handlers.common.helper import mass_notification_deletion, driver_cabinet_menu
from services.liqpay import refund_payment, payment_completion
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser
from state.user import OrderTaxi
from state.driver import OrderDriver
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from state.user import UserCabinetStates
from bot import bot
import texts
from utils.template_engine import render_template
from texts.keyboards import OPEN_MENU
from handlers.common.helper import driver_cabinet_menu
from bot import dp
import time


async def accept_order(callback: types.CallbackQuery, state: FSMContext):
    callback_data = json.loads(callback.data)
    order_id = callback_data.get('id')
    chat_id = callback.message.chat.id
    message = callback.message

    response = await HttpOrder.accept_order(data={
        "driver_chat_id": chat_id,
        "order_id": order_id
    })
    if response.get('response_code') != 200:
        return await bot.send_message(chat_id=chat_id, text=texts.SERVER_ERROR)

    order_data = response.get('response_data').get('data')
    await state.update_data(order_data=order_data)

    await message.answer(text=texts.ASKING_TAKE_SUCCESSFUL, reply_markup=ReplyKeyboardRemove())

    template = render_template("arrival_time.js2", data=order_data)
    await message.answer(text=template, reply_markup=order_arrival_time)


async def skip_order(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


async def take_arrival_time(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    callback_data = json.loads(callback.data)
    arrival_time = callback_data.get('arrival_time')
    order_data['arrival_time'] = arrival_time
    passenger_id = order_data.get('user_chat_id')
    msg_order_notification = []

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    template = render_template("driver_info_for_user.js2", data=data)
    msg_driver_info = await bot.send_message(chat_id=passenger_id, text=template, reply_markup=order_menu_kb)
    msg_order_notification.append(callback.message.message_id)

    template = render_template("processing_order_info_for_driver.js2", data=order_data)
    mgs = await callback.message.answer(text=template, reply_markup=driver_order_menu)

    await state.update_data(msg_driver_info=msg_driver_info.message_id)
    await state.update_data(procesing_order_info_for_driver=mgs.message_id)


async def driver_in_place(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    msg_order_notification = []

    msg = await bot.send_message(order_data.get('user_chat_id'), text='Водій уже прибув 🎉')
    msg_order_notification.append(msg.message_id)
    msg = await bot.send_message(order_data.get('user_chat_id'), text='Якщо очікування превисить 3хв тоді '
                                                                      'кожна наступна хв буде коштувати 3 грн '
                                                                      '❗️')
    msg_order_notification.append(msg.message_id)

    msg = await callback.message.answer('Ми повідомили пасажира що ви прибули 📣')
    msg_order_notification.append(msg.message_id)
    msg_order_notification.append(callback.message.message_id)

    await state.update_data(msg_order_notification=msg_order_notification, time_wait_passenger=time.time())
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id, reply_markup=driver_order_start)


async def sure_cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Ви впевнені що бажаєте скасуваити замолення', reply_markup=yes_no_kb)
    await state.set_state(OrderDriver.waiting_cancel_order)


async def cancel_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    passenger_id = order_data.get('user_chat_id')
    driver_id = message.chat.id

    if data.get('msg_order_notification') is not None:
        await mass_notification_deletion([passenger_id, driver_id], data.get('msg_order_notification'))
    await bot.delete_message(passenger_id, data.get('msg_driver_info'))
    await bot.delete_message(driver_id, data.get('processing_order_info_for_driver'))

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    res = await refund_payment(order_data.get('id'))
    print(f"INFO: refund money -> {res.get('status')}")

    await bot.send_message(passenger_id, 'Водій скасував замолення 🚫')
    await message.answer('Замолення скасовано 🚫')

    await driver_cabinet_menu(state, message=message)


async def start_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
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

    msg = await callback.message.answer('Поїздку начато 🚕')
    msg_order_notification.append(msg.message_id)
    msg_order_notification.append(callback.message.message_id)

    msg = await bot.send_message(order_data.get('user_chat_id'), text='Поїздку начато 🚕',
                                 reply_markup=ReplyKeyboardRemove())
    msg_order_notification.append(msg.message_id)
    await state.update_data(msg_order_notification=msg_order_notification)
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id, reply_markup=driver_order_end)


async def end_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    passenger_id = order_data.get('user_chat_id')
    driver_id = callback.message.chat.id

    await mass_notification_deletion([driver_id, passenger_id],
                                     data.get('msg_order_notification'))
    await bot.delete_message(passenger_id, data.get('msg_driver_info'))

    passenger_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=passenger_id,
                                                                    user_id=passenger_id, bot_id=bot.id))
    await passenger_state.set_state(OrderTaxi.waiting_rate_driver)

    await callback.message.answer('Поїздку закінчено ✅')
    await bot.send_message(order_data.get('user_chat_id'), text='Поїздку закінчено ✅')
    await bot.send_message(order_data.get('user_chat_id'), text='Як пройшла поїздка?', reply_markup=rate)
    await callback.message.answer('⭐️ Оцініть поїздку з пассажиром ⭐️', reply_markup=rate)

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
    order_data = data.get('order_data')

    passenger_rate = callback_data.get('rate')
    await HttpUser.rete_user(data={
        "chat_id": order_data.get('user_chat_id'),
        "rate": int(passenger_rate)
    })

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)


async def start_message_to_passenger(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Надішліть мені повідомлення і я його перешлю пасажиру.',
                                  reply_markup=back_kb)

    await state.set_state(OrderDriver.waiting_message_to_passenger)


async def send_message_to_passenger(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    await bot.send_message(order_data.get('user_chat_id'), f'Повідомлення від водія 💬'
                                                           f'\n{message.text}', reply_markup=reply_message_to_driver)
    await message.answer('Повідомлення вітправлено ✅')


async def open_order_menu(message: types.Message, state: FSMContext):
    await message.answer('Меню замолення', reply_markup=ReplyKeyboardRemove())

    await state.set_state(OrderTaxi.waiting_menu_order)
