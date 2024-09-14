from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import json

from services.http_client import HttpOrder, HttpUser
from state.user import UserCabinetStates, EditUserInfo, OtherFun, OrderTaxi
from utils.template_engine import render_template
from aiogram.types import ReplyKeyboardRemove
from handlers.common.inline_mode import InlineHandlers
from bot import bot
from texts import TextManager, get_text_manager
from data.config import BOT_URL
from keyboards import KeyboardManager, get_kb_manager


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    if bt_text == user_text_manager.keyboards.SETTING:
        template = render_template("user_info.js2", data=data, lang_code=data.get('user_language'))
        await message.answer(text=template, reply_markup=user_kb_manager.default.users.edit_user)
        await state.set_state(EditUserInfo.waiting_edit_info)
    elif bt_text == user_text_manager.keyboards.ORDER_TAXI:
        city = data.get("city")
        await message.answer(text=user_text_manager.asking.REQUEST_DRIVER_CONFIRMATION.format(city = city),
                             reply_markup=user_kb_manager.default.users.menu_before_order)
        await state.set_state(OrderTaxi.waiting_accept_city)
    elif bt_text == user_text_manager.keyboards.HISTORY_ORDER:
        await message.answer(text=user_text_manager.asking.ORDER_HISTORY_INFO, reply_markup=ReplyKeyboardRemove())
        await message.answer(text=user_text_manager.asking.CHOOSE_ORDER, reply_markup=user_kb_manager.inline.history_order.choose_order)
        await state.set_state(UserCabinetStates.waiting_history_order)
    elif bt_text == user_text_manager.keyboards.OTHER:
        await message.answer(text=user_text_manager.asking.OTHER_INFO, reply_markup=user_kb_manager.default.users.other)

        await state.set_state(OtherFun.waiting_other_fun)
    elif bt_text == user_text_manager.keyboards.SHARE_CHATBOT:
        await message.answer(user_text_manager.asking.SHARE_LINK.format(BOT_URL=BOT_URL))


async def show_history_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpOrder.get_driver_order(data={'chat_id': data.get('chat_id')})
    orders = response.get('response_data').get('data')

    if len(orders) == 0:
        await callback.answer(
            results=[],
            switch_pm_text=user_text_manager.asking.ORDER_HISTORY_EMPTY,
            switch_pm_parameter="start"
        )
        return

    def render_func(item: dict):

        created_at = item.get('created_at')
        id = str(item.get('id'))
        template = render_template('order_history.js2', data=item, lang_code=data.get('user_language'))

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




