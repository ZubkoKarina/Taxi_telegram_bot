from pyexpat.errors import messages

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from handlers.common.helper import get_drivers, user_cabinet_menu, driver_cabinet_menu, sort_drivers
from handlers.common import message_menager
from handlers.common.message_menager import delete_messages
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser, HttpDriver, HttpOther
from state.user import OrderTaxi
from state.driver import OrderDriver
from services.liqpay import create_payment, refund_payment
from aiogram.types import ReplyKeyboardRemove
from bot import bot
from texts import TextManager, get_text_manager
from handlers.user.cabinet.common import open_menu
from bot import dp
import time
from keyboards import KeyboardManager, get_kb_manager
from .create_order import create_order
from .search_driver import search_drivers
from handlers.common.ending_route import ask_raw_message
from state import state_manager
from utils.template_engine import render_template
from handlers.driver.cabinet.common import open_order_menu as open_driver_order_menu
from handlers.user.cabinet.common import open_order_menu


async def order_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    if message.text == user_text_manager.keyboards.CANCEL_ORDER:
        await sure_cancel_order(message, state)
    elif message.text == user_text_manager.keyboards.SEARCH_AGAIN:
        await create_order(order_data)
    elif message.text == user_text_manager.keyboards.CHANGE_PRICE:
        await change_cost(message, state)
    elif message.text == user_text_manager.keyboards.OPEN_MENU:
        await user_cabinet_menu(state, message=message)
    elif message.text == user_text_manager.keyboards.REPLACE_COST:
        await wait_replace_cost(message, state)
    elif message.text == user_text_manager.keyboards.CHAT_WITH_DRIVER:
        await state.set_state(OrderTaxi.waiting_message_to_driver)
        await message.answer(user_text_manager.asking.SEND_MESSAGE_TO_DRIVER,
                             reply_markup=user_kb_manager.default.back)
    else:
        await ask_raw_message(message, state)


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

    await search_drivers(message, state)


async def change_cost(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    await delete_messages('order_messages', state)
    await bot.delete_message(message.chat.id, data.get('order_info_msg'))

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})
    await message.answer(user_text_manager.asking.WAIT_COST, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderTaxi.waiting_new_price)


async def take_cost(message: types.Message, state: FSMContext):
    cost = float(message.text)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    if float(order_data.get('cost')) > cost:
        return message.answer(user_text_manager.asking.COST_CHANGE_WARNING)
    order_data['cost'] = cost
    await message.answer(user_text_manager.asking.COST_UPDATED)

    if order_data.get('payMethod') == 'Онлайн_':
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
    print(order_data)
    await bot.send_message(chat_id=order_data.get('driver_chat_id'),
                           text=f'{user_text_manager.asking.MESSAGE_FROM_PASSENGER}\n🗣️ *{message.text}* 🗣️',
                           reply_markup=user_kb_manager.inline.order_driver.reply_message_to_passenger,
                           parse_mode='Markdown'
                           )
    await message.answer(user_text_manager.asking.MESSAGE_SEND)


async def sure_cancel_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')

    driver_chat_id = order_data.get('driver_chat_id', None)
    distance = 0
    if order_data.get('planned_order'):
        await message.answer(user_text_manager.asking.CANCEL_FAIL)
        return await open_order_menu(message, state)
    if driver_chat_id is not None:
        driver_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=driver_chat_id, user_id=driver_chat_id,
                                                                     bot_id=bot.id))
        driver_data = await driver_state.get_data()
        start_driver_geo = order_data.get('driver_geo', [0, 0])
        now_driver_geo = driver_data.get('geo', [0, 0])
        distance = haversine(now_driver_geo, start_driver_geo)

        elapsed_time = (time.time() - order_data.get('time_order_accept', time.time())) / 60

        if elapsed_time >= 3:
            await message.answer(user_text_manager.asking.CANCEL_FAIL)
            return await open_order_menu(message, state)
        elif distance >= 1:
            await message.answer(user_text_manager.asking.CANCEL_FAIL)
            return await open_order_menu(message, state)

    await message.answer(user_text_manager.asking.ORDER_CANCEL_CONFIRMATION, reply_markup=user_kb_manager.default.yes_no)
    await state.set_state(OrderTaxi.waiting_cancel_order)


async def cancel_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    order_data = data.get('order_data')
    search_info = data.get('search_info')

    await delete_messages('order_messages', state)
    await bot.delete_message(message.chat.id, data.get('order_info_msg'))
    if order_data.get('driver_chat_id') is not None:
        driver_id = order_data.get('driver_chat_id')
        driver_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=driver_id,
                                                                     user_id=driver_id, bot_id=bot.id))
        driver_msg = await bot.send_message(driver_id, user_text_manager.asking.ORDER_CANCELLED_BY_PASSENGER)

        await message_menager.delete_messages('order_messages', driver_state)
        await driver_cabinet_menu(driver_state, message=driver_msg)

    await HttpOrder.cancel_order(data={"order_id": int(order_data.get('id'))})

    await message.answer(user_text_manager.asking.ORDER_CANCELLED)

    await open_menu(message, state)


async def wait_replace_cost(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')

    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await message.answer(user_text_manager.asking.WAIT_REPLACE_COST, reply_markup=user_kb_manager.default.back)

    await state.set_state(OrderTaxi.waiting_replace_cost)


async def take_replace_cost(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    driver_chat_id: int = order_data.get('driver_chat_id')
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    driver_language = await state_manager.get_element_from_user_data(driver_chat_id, 'user_language')

    driver_kb_manager: KeyboardManager = get_kb_manager(driver_language)

    if message.text == user_text_manager.keyboards.BACK:
        await open_order_menu(message, state)
    new_cost: int = message.text
    order_data['new_cost'] = new_cost

    template = render_template("replace_cost.js2",
                               data={'old_cost': order_data.get('cost'), 'new_cost': new_cost},
                               lang_code=driver_language)
    await bot.send_message(chat_id=driver_chat_id, text=template, reply_markup=driver_kb_manager.default.yes_no)
    await state_manager.set_user_state(driver_chat_id, OrderDriver.waiting_accept_replace_cost)
    await message.answer(text=user_text_manager.asking.WAIT_ACCEPT_DRIVER_REPLACE_COST, reply_markup=ReplyKeyboardRemove())

    await state.update_data(new_cost=new_cost)


async def take_status_replace_cost(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_data = data.get('order_data')
    driver_chat_id: int = order_data.get('driver_chat_id')
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    driver_language = await state_manager.get_element_from_user_data(driver_chat_id, 'user_language')
    driver_text_manager: TextManager = get_text_manager(driver_language)

    new_cost: int = await state_manager.get_element_from_user_data(driver_chat_id, 'new_cost')

    if message.text == user_text_manager.keyboards.NO:
        msg_to_driver = await bot.send_message(chat_id=driver_chat_id,
                                               text=driver_text_manager.asking.NO_ACCEPT_REPLACE_COST)
        await message.answer(user_text_manager.asking.NO_ACCEPT_REPLACE_COST)
    else:
        await HttpOrder.update_order({'order_id': order_data.get('id'), 'cost': int(new_cost)})

        msg_to_driver = await bot.send_message(chat_id=driver_chat_id, text=driver_text_manager.asking.ACCEPT_REPLACE_COST)
        await message.answer(user_text_manager.asking.ACCEPT_REPLACE_COST)

    await open_order_menu(message, state)

    driver_state: FSMContext = await state_manager.get_user_state(driver_chat_id)
    await open_driver_order_menu(msg_to_driver, driver_state)

