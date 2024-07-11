from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import json

from keyboards.default.users.menu import user_menu_text
from handlers.common.helper import get_drivers, user_cabinet_menu
from handlers.common.inline_mode import InlineHandlers
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser
from keyboards.inline.history_order import choose_order
from keyboards.default.users.setting import edit_user
from keyboards.default.users.other import other_kb
from keyboards.default.yes_no import yes_no_kb
from state.user import UserCabinetStates, EditUserInfo, OtherFun, OrderTaxi
from utils.template_engine import render_template
from aiogram.types import ReplyKeyboardRemove
from bot import bot
import texts
from texts.keyboards import OPEN_MENU


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text
    data = await state.get_data()

    if bt_text == user_menu_text['setting']:
        template = render_template("user_info.js2", data=data)
        await message.answer(text=template, reply_markup=edit_user)
        await state.set_state(EditUserInfo.waiting_edit_info)
    elif bt_text == user_menu_text['order_taxi']:
        await message.answer(text=f'Ви бажаєте замовити таксі в {data.get('City')}?', reply_markup=yes_no_kb)
        await state.set_state(OrderTaxi.waiting_accept_city)
    elif bt_text == user_menu_text['history_order']:
        await message.answer(text='Тут ви сможите переглаянути історію ваших поїздок та їх деталі', reply_markup=ReplyKeyboardRemove())
        await message.answer(text='Оберіть зі списку ваше замоленя 👇', reply_markup=choose_order)
        await state.set_state(UserCabinetStates.waiting_history_order)
    elif bt_text == user_menu_text['reference_info']:
        await message.answer(text='Тут ви сможите вітправити заявку на водія та інше...', reply_markup=other_kb)

        await state.set_state(OtherFun.waiting_other_fun)


async def show_history_order(callback: types.InlineQuery, state: FSMContext):
    user_data = await state.get_data()
    response = await HttpOrder.get_user_order(data={'chat_id': user_data.get('chat_id')})
    orders = response.get('response_data').get('data')

    def render_func(item: dict):
        print(type(item))
        shipping_address = item.get('shipping_address')
        id = str(item.get('id'))

        return types.InlineQueryResultArticle(
            id=id,
            title=shipping_address,
            input_message_content=types.InputTextMessageContent(
                message_text=shipping_address
            ),
        )

    return await InlineHandlers.generate_inline_list(
        callback, data=orders, render_func=render_func
    )




