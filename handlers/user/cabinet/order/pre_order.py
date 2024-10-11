from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey

from handlers.common import message_menager
from services.http_client import HttpOrder, HttpUser, HttpDriver, HttpOther
from state.user import OrderTaxi
from texts import TextManager, get_text_manager
from utils.template_engine import render_template
from keyboards import KeyboardManager, get_kb_manager
from .create_order import create_order

async def asking_pre_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpOrder.get_user_order(data={'chat_id': message.chat.id})
    user_orders = response.get('response_data').get('data')
    if len(user_orders) == 0:
        return message.answer(user_text_manager.asking.PRE_ORDER_NOT_FOUND)
    last_user_order = user_orders[-1]

    template = render_template("order_passenger/pre_order.js2", data=last_user_order, lang_code=data.get('user_language'))

    message = await message.answer(template, reply_markup=user_kb_manager.default.users.pre_order)
    await message_menager.add_to_message_list(message, state, 'order_messages', 'pre_order')

    await state.set_state(OrderTaxi.waiting_create_pre_order)

async def create_pre_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpOrder.get_user_order(data={'chat_id': message.chat.id})
    user_orders = response.get('response_data').get('data')
    last_user_order = user_orders[-1]
    last_user_order['driver_chat_id'] = None

    await message_menager.delete_messages(data.get('messages_order'), state)
    await create_order(last_user_order)