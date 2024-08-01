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
from handlers.common.inline_mode import InlineHandlers
from bot import bot
import texts
from texts.keyboards import OPEN_MENU
from data.config import BOT_URL


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text
    data = await state.get_data()

    if bt_text == user_menu_text['setting']:
        template = render_template("user_info.js2", data=data)
        await message.answer(text=template, reply_markup=edit_user)
        await state.set_state(EditUserInfo.waiting_edit_info)
    elif bt_text == user_menu_text['order_taxi']:
        await message.answer(text=f'Ви бажаєте замовити таксі в {data.get("city")}?', reply_markup=yes_no_kb)
        await state.set_state(OrderTaxi.waiting_accept_city)
    elif bt_text == user_menu_text['history_order']:

        await message.answer(text='Тут ви сможите переглаянути історію ваших поїздок та їх деталі', reply_markup=ReplyKeyboardRemove())
        await message.answer(text='Оберіть зі списку ваше замоленя 👇', reply_markup=choose_order)
        await state.set_state(UserCabinetStates.waiting_history_order)
    elif bt_text == user_menu_text['reference_info']:
        await message.answer(text='Тут ви сможите вітправити заявку на водія та інше...', reply_markup=other_kb)

        await state.set_state(OtherFun.waiting_other_fun)
    elif bt_text == user_menu_text['share_chatbot']:
        await message.answer(f'Ось посилання для ваших друзів 😊\n{BOT_URL}')

async def show_history_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    response = await HttpOrder.get_driver_order(data={'chat_id': data.get('chat_id')})
    orders = response.get('response_data').get('data')

    if len(orders) == 0:
        await callback.answer(
            results=[],
            switch_pm_text="Історія замовлень порожня",
            switch_pm_parameter="start"
        )
        return

    def render_func(item: dict):

        created_at = item.get('created_at')
        id = str(item.get('id'))
        template = render_template('order_history.js2', data=item)

        return types.InlineQueryResultArticle(
            id=id,
            title=created_at,
            input_message_content=types.InputTextMessageContent(
                message_text=template
            ),
        )

    return await InlineHandlers.generate_inline_list(
        callback, data=orders, render_func=render_func
    )




