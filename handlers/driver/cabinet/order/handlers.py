from pyexpat.errors import messages

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from rapidfuzz.distance.OSA import distance
from requests import request

from handlers.common.helper import driver_cabinet_menu, user_cabinet_menu
from handlers.common import message_menager
from handlers.user.cabinet.order.planned_order import start_planned_order as start_planned_order_passenger
from keyboards.default.en.users import menu_properties
from services.liqpay import refund_payment, payment_completion
from services.google_maps import geocode_place_by_name, geocode_place_by_geo
from utils import build_route
from services.http_client import HttpOrder, HttpUser, HttpOther, HttpDriver
from state.user import OrderTaxi
from state.driver import OrderDriver
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from state import state_manager
from bot import bot
from texts import TextManager, get_text_manager
from utils.template_engine import render_template
from handlers.common.helper import driver_cabinet_menu, get_drivers
from services.visicom import get_place_by_geo
from bot import dp
from utils.distance_calculation import haversine
import time
from keyboards import KeyboardManager, get_kb_manager
from datetime import datetime, timedelta
from handlers.user.cabinet.common import open_order_menu as open_passenger_order_menu
from handlers.driver.cabinet.common import open_order_menu


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
        return await bot.send_message(chat_id=chat_id, text=user_text_manager.asking.ACCEPT_ORDER_FAIL)

    order_data = response.get('response_data').get('data')
    await state.update_data(order_data=order_data)
    if order_data.get('planned_order') is not None:
        await message.answer(user_text_manager.asking.PLANNED_ORDER_SUCCESSFUL)
        return
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
    message = callback.message

    order_data['time_take_order'] = time.time()

    passenger_id = order_data.get('user_chat_id')
    passenger_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=passenger_id, user_id=passenger_id, bot_id=bot.id))
    passenger_data = await passenger_state.get_data()
    passenger_language = passenger_data.get('user_language')
    passenger_text_manager: TextManager = get_text_manager(passenger_data.get('user_language'))
    passenger_kb_manager: KeyboardManager = get_kb_manager(passenger_data.get('user_language'))

    order_data['passenger_language'] = passenger_language

    await callback.message.delete()

    template = render_template("order_passenger/driver_info.js2", data={**data, 'arrival_time': arrival_time}, lang_code=passenger_language)
    msg = await bot.send_message(chat_id=passenger_id, text=template, reply_markup=passenger_kb_manager.inline.order.tracking_driver_app)
    await bot.send_message(chat_id=passenger_id, text=passenger_text_manager.asking.LIVE_LOCATION_DRIVER, reply_markup=passenger_kb_manager.default.users.order_menu)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'driver_info')

    response = await HttpUser.get_user_info({'chat_id': passenger_id})
    user_data = response.get('response_data').get('data')

    template = render_template("order_driver/order_info_processing.js2",
                               data={**order_data, 'arrival_time': arrival_time, 'passenger_name': user_data.get('name')}, lang_code=data.get('user_language'))
    msg = await callback.message.answer(text=template, reply_markup=user_kb_manager.inline.order_driver.menu)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'order_info_processing')

    await state.update_data(order_data=order_data)


async def start_planned_order(callback: types.CallbackQuery, state: FSMContext):
    callback_data = json.loads(callback.data)
    order_id = callback_data.get('id')
    chat_id = callback.message.chat.id
    message = callback.message

    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    await message_menager.delete_messages('order_planned_messages', state)

    response = await HttpOrder.get_order(data={
        "order_id": order_id
    })
    if response.get('response_code') != 200:
        return await bot.send_message(chat_id=chat_id, text=user_text_manager.services.SERVER_ERROR)

    order_data = response.get('response_data').get('data')
    order_data['time_take_order'] = 1
    passenger_id = order_data.get('user_chat_id')

    passenger_state: FSMContext = FSMContext(dp.storage,
                                             StorageKey(chat_id=passenger_id, user_id=passenger_id, bot_id=bot.id))

    passenger_data = await passenger_state.get_data()
    passenger_language = passenger_data.get('user_language')
    order_data['passenger_language'] = passenger_language

    response = await HttpUser.get_user_info({'chat_id': passenger_id})
    user_data = response.get('response_data').get('data')

    template = render_template("order_driver/order_info_processing.js2",
                               data={**order_data, 'passenger_name': user_data.get('name')},
                               lang_code=data.get('user_language'))
    msg = await callback.message.answer(text=template, reply_markup=user_kb_manager.inline.order_driver.menu)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'order_info_processing')

    await start_planned_order_passenger(order_id)

    await state.update_data(order_data=order_data)


async def cancel_planned_order(callback: types.CallbackQuery, state: FSMContext):
    callback_data = json.loads(callback.data)
    order_id = callback_data.get('id')
    chat_id = callback.message.chat.id

    message = callback.message
    is_minute = 0

    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpOrder.get_order(data={
        "order_id": order_id
    })
    if response.get('response_code') != 200:
        return await bot.send_message(chat_id=chat_id, text=user_text_manager.services.SERVER_ERROR)
    order_data = response.get('response_data').get('data')

    passenger_id = int(order_data.get('user_chat_id'))
    date_order = order_data.get('planned_order').get('date')
    time_order = order_data.get('planned_order').get('time')

    start_time = datetime.strptime(f"{date_order} {time_order}", "%d.%m.%Y %H:%M")
    if (start_time - timedelta(minutes=10)) <= datetime.now():
        is_minute = 1

    start_point_geo = [float(order_data.get('start_point').get('geo_lat')), float(order_data.get('start_point').get('geo_lng'))]
    distance_to_start_point = haversine(data.get('geo'), start_point_geo)
    if (start_time - timedelta(minutes=30)) <= datetime.now() and distance_to_start_point >= 5:
        is_minute = 1

    if is_minute == 1:
        await message.answer(user_text_manager.asking.ALERT_CANCEL_ORDER)

    request_data = {"order_id": int(order_data.get('id')), "status_id": 6,
                    'driver_chat_id': chat_id, 'is_minute': is_minute}
    await HttpOrder.cancel_order_by_driver(data=request_data)
    response = await HttpDriver.get_driver_info(data={'chat_id': chat_id})
    is_banned = response.get('response_data').get('data').get('user').get('is_banned')

    if is_banned:
        await message.answer(user_text_manager.services.USER_BANNED)
        await state.clear()
        return

    passenger_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=passenger_id,
                                                                    user_id=passenger_id, bot_id=bot.id))
    passenger_data = await passenger_state.get_data()
    passenger_text_manager: TextManager = get_text_manager(passenger_data.get('user_language'))

    msg_passenger = await bot.send_message(passenger_id, passenger_text_manager.asking.CANCELLED_BY_DRIVER)
    await message.answer(user_text_manager.asking.ORDER_CANCELLED)
    await callback.message.delete()
    await user_cabinet_menu(passenger_state, message=msg_passenger)


async def driver_in_place(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    passenger_text_manager: TextManager = get_text_manager(order_data.get('passenger_language'))

    response =  await HttpOther.get_variable()
    price_wait = float(response.get('response_data').get('variable').get('k', 3.00))
    order_data['price_wait'] = price_wait

    msg = await bot.send_message(order_data.get('user_chat_id'), text=passenger_text_manager.asking.DRIVER_ARRIVED)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'driver_in_place')
    msg = await bot.send_message(order_data.get('user_chat_id'), text=passenger_text_manager.asking.EXTRA_WAITING_COST.format(price_wait))
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'driver_in_place')

    msg = await callback.message.answer(user_text_manager.asking.PASSENGER_NOTIFIED)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'driver_in_place')
    await message_menager.add_to_message_list(callback.message, state, 'order_messages')

    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        reply_markup=user_kb_manager.inline.order_driver.start)

    await state.update_data(time_wait_passenger=time.time(), order_data=order_data)


async def sure_cancel_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await callback.message.answer(user_text_manager.asking.ORDER_CANCEL_CONFIRMATION, reply_markup=user_kb_manager.default.yes_no)
    await state.set_state(OrderDriver.waiting_cancel_order)


async def cancel_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    passenger_text_manager: TextManager = get_text_manager(order_data.get('passenger_language'))

    passenger_id = order_data.get('user_chat_id')
    driver_id = message.chat.id

    await message_menager.delete_messages('order_messages', state)

    is_minute = ((time.time() - order_data.get('time_take_order')) / 60) > 1
    if is_minute:
        await message.answer(user_text_manager.asking.ALERT_CANCEL_ORDER)
        is_minute = 1
    else:
        is_minute = 0

    request_data = {"order_id": int(order_data.get('id')), "status_id": 6,
                                                 'driver_chat_id': driver_id, 'is_minute': is_minute}

    await HttpOrder.cancel_order_by_driver(data=request_data)
    response = await HttpDriver.get_driver_info(data={'chat_id': int(driver_id)})

    is_banned = response.get('response_data').get('data').get('user').get('is_banned')

    if is_banned:
        await message.answer(user_text_manager.services.USER_BANNED)
        await state.clear()
        return

    passenger_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=passenger_id,
                                                                    user_id=passenger_id, bot_id=bot.id))

    msg_passenger = await bot.send_message(passenger_id, passenger_text_manager.asking.CANCELLED_BY_DRIVER)
    await message.answer(user_text_manager.asking.ORDER_CANCELLED)

    await driver_cabinet_menu(state, message=message)
    await user_cabinet_menu(passenger_state, message=msg_passenger)


async def start_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    passenger_text_manager: TextManager = get_text_manager(order_data.get('passenger_language'))
    passenger_kb_manager: KeyboardManager = get_kb_manager(order_data.get('passenger_language'))

    passenger_id = order_data.get('user_chat_id')
    driver_id = callback.message.chat.id

    await message_menager.delete_messages('order_messages', state, 'driver_in_place')

    time_wait_passenger = data.get('time_wait_passenger')
    elapsed_time = round(((time.time() - time_wait_passenger) / 60), 2)
    pay_time_wait_passenger = (round(((time.time() - time_wait_passenger) / 60), 2) - 3)

    if elapsed_time >= 3:
        cost = float(order_data.get('cost'))
        cost_wait = (elapsed_time * order_data.get('price_wait'))
        cost = cost + cost_wait
        await HttpOrder.update_order(data={
            'order_id': order_data.get('id'),
            'cost': round(cost, 2)
        })

        template = render_template("order_passenger/cost_up_by_wait.js2",
                                   data={'time_wait_passenger': elapsed_time, 'price_wait': order_data.get('price_wait'),
                                         'new_cost': cost, 'cost_wait': cost_wait,
                                         'pay_time_wait_passenger': pay_time_wait_passenger},
                                   lang_code=order_data.get('passenger_language'))
        await bot.send_message(chat_id=passenger_id, text=template)

    msg = await callback.message.answer(user_text_manager.asking.TRIP_STARTED)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'start_order')

    msg = await bot.send_message(order_data.get('user_chat_id'), passenger_text_manager.asking.TRIP_STARTED,
                                 reply_markup=passenger_kb_manager.default.users.order_processing)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'start_order')

    if len(order_data.get('additional_point')) != 0:
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                            message_id=callback.message.message_id,
                                            reply_markup=user_kb_manager.inline.order_driver.end_with_additional_point)
    else:
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                            message_id=callback.message.message_id,
                                            reply_markup=user_kb_manager.inline.order_driver.end)


async def end_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    passenger_text_manager: TextManager = get_text_manager(order_data.get('passenger_language'))

    passenger_id = order_data.get('user_chat_id')
    driver_id = callback.message.chat.id

    await message_menager.delete_messages('order_messages', state)

    passenger_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=passenger_id,
                                                                    user_id=passenger_id, bot_id=bot.id))
    await passenger_state.set_state(OrderTaxi.waiting_rate_driver)

    await callback.message.answer(user_text_manager.asking.TRIP_ENDED)
    await bot.send_message(order_data.get('user_chat_id'), text=passenger_text_manager.asking.TRIP_ENDED)
    await bot.send_message(order_data.get('user_chat_id'), text=passenger_text_manager.asking.RATE_TRIP, reply_markup=user_kb_manager.inline.order.rate)
    await callback.message.answer(user_text_manager.asking.RATE_PASSENGER, reply_markup=user_kb_manager.inline.order.rate)

    if order_data.get('payMethod') == 'Онлайн_':
        res = await payment_completion(order_data.get('id'))
        print(f"INFO: payment completion -> {res.get('status')}")

    await HttpOrder.complete_order({
        "user_chat_id": int(passenger_id),
        "driver_chat_id": int(driver_id),
        "order_id": int(order_data.get('id'))
    })

    response = await HttpDriver.get_driver_info({'chat_id': driver_id})
    driver_wallet: int = response.get('response_data').get('data').get('wallet')
    if int(driver_wallet) <= 0:
        await callback.message.answer(user_text_manager.asking.TOP_UP_BALANCE)
        await HttpDriver.set_active_driver({'chat_id': driver_id})

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
    order_data = data.get('order_data')

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    passenger_text_manager: TextManager = get_text_manager(order_data.get('passenger_language'))

    print(f'USER CHAT ID: {order_data.get("user_chat_id")}')
    await bot.send_message(chat_id=order_data.get('user_chat_id'),
                           text=f"{passenger_text_manager.asking.MESSAGE_FROM_DRIVER}️\n👨‍✈️ *{message.text}* 👨‍✈️",
                           reply_markup=user_kb_manager.inline.order.reply_message_to_driver,
                           parse_mode='Markdown')
    await message.answer(user_text_manager.asking.MESSAGE_SEND)


async def choice_type_navigation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    point_geo_list = []

    if callback.data == 'open_navigation_to':
        start_point = order_data.get('start_point')
        point_geo_list.append((start_point.get('geo_lat'), start_point.get('geo_lng')))

    elif callback.data == 'open_navigation_from':
        additional_point = order_data.get('additional_point')
        end_point = order_data.get('end_point')
        point_geo_list = [(item.get('geo_lat'), item.get('geo_lng')) for item in additional_point]
        point_geo_list.append((end_point.get('geo_lat'), end_point.get('geo_lng')))

    waze_url = build_route.build_waze_route(point_geo_list)
    google_url = build_route.build_google_maps_route(point_geo_list)

    choice_type_navigation_kb = user_kb_manager.inline.navigation.generation_buttons_navigation(google_url, waze_url)

    await callback.message.answer(user_text_manager.asking.NAVIGATION_METHOD_CHOICE, reply_markup=choice_type_navigation_kb)


async def sos(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await callback.message.answer(text=user_text_manager.asking.SOS_COMMENT)
    await state.set_state(OrderDriver.waiting_sos_comment)


async def send_sos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    main_driver_geo = data.get('geo')

    driver_place = get_place_by_geo(main_driver_geo[0], main_driver_geo[1])

    drivers = await get_drivers(region=data.get('region'))
    for driver in drivers:
        if driver.get('geo') is not None:
            distance_driver = haversine(main_driver_geo, driver.get('geo'))
        else:
            distance_driver = 1000
        if distance_driver <= 10:

            template = render_template("order_driver/sos.js2",
                                       data={'phone_number': data.get('phone_number'), 'comment': message.text, 'place': driver_place.get('address', 'Не визначено')},
                                       lang_code=data.get('user_language'))
            await bot.send_message(text=template, chat_id=driver.get('chat_id'))

    await HttpOther.send_sos(data={
                                    "chat_id" : message.chat.id,
                                    "comment" : message.text,
                                    "location" : driver_place.get('address', 'Не визначено'),
                                    "is_driver" : 1
                                })

    await message.answer(text=user_text_manager.asking.SOS_SEND)
    await state.set_state(OrderDriver.waiting_menu_order)


async def additional_point_wait(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    passenger_text_manager: TextManager = get_text_manager(order_data.get('passenger_language'))

    await state.update_data(time_wait_passenger=time.time())

    await callback.message.answer(user_text_manager.asking.ON_TIMER, )
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        reply_markup=user_kb_manager.inline.order_driver.end_with_off_timer)

    msg = await bot.send_message(order_data.get('user_chat_id'), text=passenger_text_manager.asking.ON_TIMER)
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'additional_point')
    msg = await bot.send_message(order_data.get('user_chat_id'), text=passenger_text_manager.asking.EXTRA_WAITING_COST.format(order_data.get('price_wait')))
    await message_menager.add_to_message_list(msg, state, 'order_messages', 'additional_point')


async def end_additional_point_wait(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    passenger_text_manager: TextManager = get_text_manager(order_data.get('passenger_language'))

    passenger_id = order_data.get('user_chat_id')
    await message_menager.delete_messages('order_messages', state, 'additional_point')

    time_wait_passenger = data.get('time_wait_passenger')
    elapsed_time = round(((time.time() - time_wait_passenger) / 60), 2)
    pay_time_wait_passenger = (round(((time.time() - time_wait_passenger) / 60), 2) - 3)

    if elapsed_time >= 3:
        cost = float(order_data.get('cost'))
        cost_wait = (elapsed_time * order_data.get('price_wait'))
        cost = cost + cost_wait
        await HttpOrder.update_order(data={
            'order_id': order_data.get('id'),
            'cost': round(cost, 2)
        })

        template = render_template("order_passenger/cost_up_by_wait.js2",
                                   data={'time_wait_passenger': elapsed_time,
                                         'price_wait': order_data.get('price_wait'), 'new_cost': cost,
                                         'cost_wait': cost_wait, 'pay_time_wait_passenger': pay_time_wait_passenger},
                                   lang_code=order_data.get('passenger_language'))
        await bot.send_message(chat_id=passenger_id, text=template)

    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        reply_markup=user_kb_manager.inline.order_driver.end_with_additional_point)


async def wait_replace_cost(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await callback.message.answer(user_text_manager.asking.WAIT_REPLACE_COST, reply_markup=user_kb_manager.default.back)

    await state.set_state(OrderDriver.waiting_replace_cost)


async def take_replace_cost(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    passenger_chat_id: int = order_data.get('user_chat_id')
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    passenger_kb_manager: KeyboardManager = get_kb_manager(order_data.get('passenger_language'))

    if message.text == user_text_manager.keyboards.BACK:
        await open_order_menu(message, state)
    new_cost: int = message.text

    template = render_template("replace_cost.js2",
                               data={'old_cost': order_data.get('cost'), 'new_cost': new_cost},
                               lang_code=order_data.get('passenger_language'))
    await bot.send_message(chat_id=passenger_chat_id, text=template, reply_markup=passenger_kb_manager.default.yes_no)
    await state_manager.set_user_state(passenger_chat_id, OrderTaxi.waiting_accept_replace_cost)
    await message.answer(text=user_text_manager.asking.WAIT_ACCEPT_PASSENGER_REPLACE_COST,
                         reply_markup=ReplyKeyboardRemove())

    await state.update_data(new_cost=new_cost)


async def take_status_replace_cost(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    passenger_chat_id: int = order_data.get('user_chat_id')
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    passenger_text_manager: TextManager = get_text_manager(order_data.get('passenger_language'))
    passenger_kb_manager: KeyboardManager = get_kb_manager(order_data.get('passenger_language'))
    print(order_data)

    new_cost: int = await state_manager.get_element_from_user_data(passenger_chat_id, 'new_cost')

    if message.text == user_text_manager.keyboards.NO:
        await bot.send_message(chat_id=passenger_chat_id, text=passenger_text_manager.asking.NO_ACCEPT_REPLACE_COST,
                                reply_markup=passenger_kb_manager.default.users.order_processing)
        await message.answer(user_text_manager.asking.NO_ACCEPT_REPLACE_COST)
    else:
        print({'id': order_data.get('id'), 'cost': new_cost})
        await HttpOrder.update_order({'order_id': order_data.get('id'), 'cost': int(new_cost)})

        await bot.send_message(chat_id=passenger_chat_id, text=passenger_text_manager.asking.ACCEPT_REPLACE_COST,
                              reply_markup=passenger_kb_manager.default.users.order_processing)
        await message.answer(user_text_manager.asking.ACCEPT_REPLACE_COST)

    await open_order_menu(message, state)
    await state_manager.set_user_state(passenger_chat_id, OrderTaxi.waiting_menu_order)


