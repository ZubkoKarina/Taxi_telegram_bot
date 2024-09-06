from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import asyncio
from texts import TextManager, get_text_manager
from state.driver import DriverCabinetStates, EditDriver
from services.http_client import HttpDriver, HttpOrder
from handlers.common.helper import driver_cabinet_menu
from bot import bot
from utils.template_engine import render_template
from handlers.common.inline_mode import InlineHandlers
from keyboards import KeyboardManager, get_kb_manager


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    if bt_text == user_text_manager.keyboards.ACTIVATE_DRIVER:
        await message.answer(user_text_manager.asking.SHARE_GEO)
        await state.set_state(DriverCabinetStates.waiting_geo)
    if bt_text == user_text_manager.keyboards.DEACTIVATE_DRIVER:
        await quit_to_line(message, state)
    if bt_text == user_text_manager.keyboards.INFO:
        await driver_info(message, state)
    if bt_text == user_text_manager.keyboards.SETTING:
        template = render_template("user_info.js2", data=data, lang_code=data.get('user_language'))
        await message.answer(text=template, reply_markup=user_kb_manager.default.driver.edit_driver)
        await state.set_state(EditDriver.waiting_edit_menu)
    elif bt_text == user_text_manager.keyboards.HISTORY_ORDER:
        await state.update_data(chat_id=message.chat.id)
        await message.answer(text=user_text_manager.asking.ORDER_HISTORY_INFO, reply_markup=ReplyKeyboardRemove())
        await message.answer(text=user_text_manager.asking.CHOOSE_ORDER, reply_markup=user_kb_manager.inline.history_order.choose_order)
        await state.set_state(DriverCabinetStates.waiting_history_order)


async def quit_to_line(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    msg_id_geo = data.get('msg_id_geo')
    try:
        await bot.delete_message(message.chat.id, msg_id_geo)
    except:
        pass
    
    response = await HttpDriver.set_deactive_driver(data={
        'chat_id': message.chat.id
    })
    driver_data = response.get('response_data').get('data')
    if response.get('response_code') != 200 and driver_data.get('is_banned'):
        await driver_cabinet_menu(state, message=message)
        return
    await state.set_data({**driver_data, 'user_language': data.get('user_language')})
    await message.answer(user_text_manager.asking.GOT_OFF_LINE)

    await driver_cabinet_menu(state, message=message)


async def access_to_line(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    if message.location.live_period is None:
        return await message.answer(user_text_manager.asking.INCORRECT_GEO_PROVISION)
    if message.location.live_period <= 28800:
        return await message.answer(user_text_manager.asking.INCORRECT_TIME_GEO)

    response = await HttpDriver.set_active_driver(data={
        'chat_id': message.chat.id
    })
    driver_data = response.get('response_data').get('data')
    if response.get('response_code') != 200 or driver_data.get('is_banned'):
        await driver_cabinet_menu(state, message=message)
        return

    await state.set_data({**driver_data, 'user_language': data.get('user_language')})
    await state.update_data(geo=[lat, lon], msg_id_geo=message.message_id)

    await message.answer(user_text_manager.asking.GOT_ON_LINE)
    await message.answer(user_text_manager.asking.WAITING_ORDER,
                         reply_markup=user_kb_manager.default.driver.menu)

    await state.set_state(DriverCabinetStates.waiting_menu)


async def tracking_location(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    msg_id_geo = data.get('msg_id_geo')

    if message.message_id != msg_id_geo:
        return
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(geo=[lat, lon])


async def driver_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    template = render_template("driver_info.js2", data=data, lang_code=data.get('user_language'))

    await message.answer(template)


async def show_history_order(callback: types.InlineQuery, state: FSMContext):
    user_data = await state.get_data()
    user_text_manager: TextManager = user_data.get('user_text_manager')
    user_kb_manager: KeyboardManager = user_data.get('user_kb_manager')
    response = await HttpOrder.get_driver_order(data={'chat_id': user_data.get('chat_id')})
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
        template = render_template('order_history.js2', data=item, lang_code=user_data.get('user_language'))

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
