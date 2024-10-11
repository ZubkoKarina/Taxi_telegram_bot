import time

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
from handlers.common import message_menager
from handlers.common.ending_route import ask_raw_message


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    if bt_text == user_text_manager.keyboards.ACTIVATE_DRIVER:
        response = await HttpDriver.get_driver_info({'chat_id': message.chat.id})
        driver_data = response.get('response_data').get('data')
        await state.set_data({**driver_data, 'user_language': data.get('user_language'), 'chat_id': message.chat.id})

        if float(driver_data.get('wallet')) <= 0:
            await message.answer(user_text_manager.asking.TOP_UP_BALANCE)
            return
        await message.answer(user_text_manager.asking.SHARE_GEO, reply_markup=ReplyKeyboardRemove())
        await state.set_state(DriverCabinetStates.waiting_geo)
    elif bt_text == user_text_manager.keyboards.DEACTIVATE_DRIVER:
        await quit_to_line(message, state)
    elif bt_text == user_text_manager.keyboards.INFO:
        await driver_info(message, state)
    elif bt_text == user_text_manager.keyboards.SETTING:
        template = render_template("user_info.js2", data=data, lang_code=data.get('user_language'))
        await message.answer(text=template, reply_markup=user_kb_manager.default.driver.edit_driver)
        await state.set_state(EditDriver.waiting_edit_menu)
    elif bt_text == user_text_manager.keyboards.HISTORY_ORDER:
        await state.update_data(chat_id=message.chat.id)
        await message.answer(text=user_text_manager.asking.ORDER_HISTORY_INFO, reply_markup=ReplyKeyboardRemove())
        await message.answer(text=user_text_manager.asking.CHOOSE_ORDER, reply_markup=user_kb_manager.inline.history_order.choose_order)
        await state.set_state(DriverCabinetStates.waiting_history_order)
    elif bt_text == user_text_manager.keyboards.PLANNED_ORDER_LIST:
        await output_planned_orders(message, state)
    else:
        await ask_raw_message(message, state)


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

    # if message.location.live_period is None:
    #     return await message.answer(user_text_manager.asking.INCORRECT_GEO_PROVISION)
    # if message.location.live_period <= 28800:
    #     return await message.answer(user_text_manager.asking.INCORRECT_TIME_GEO)

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

    time_test = data.get('test_time')
    print(time_test)
    if time_test:
        elipse_time = time.time() - time_test
        print(elipse_time)

    if message.message_id != msg_id_geo:
        return
    lat = message.location.latitude
    lon = message.location.longitude

    await state.update_data(geo=[lat, lon], test_time=time.time())


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
        user_kb_manager_: KeyboardManager =  get_kb_manager(user_data.get('user_language'))

        return types.InlineQueryResultArticle(
            id=id,
            title=created_at,
            input_message_content=types.InputTextMessageContent(
                message_text=template
            ),
            reply_markup=user_kb_manager_.inline.open_menu.open_menu

        )

    return await InlineHandlers.generate_inline_list(
        callback, data=orders, render_func=render_func
    )


async def output_planned_orders(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    response = await HttpOrder.get_planned_order_for_driver(data={'chat_id': message.chat.id})
    orders = response.get('response_data').get('data')
    if len(orders) == 0:
        await message.answer(user_text_manager.asking.NOTHING_PLANNED_ORDER)

    for order in orders:
        template = render_template("order_driver/order_info.js2",
                                   data={**order, 'time_order': order.get('planned_order').get('time'),
                                         'date_order': order.get('planned_order').get('date')},
                                   lang_code=data.get('user_language'))
        msg = await message.answer(text=template, reply_markup=user_kb_manager.inline.order.generation_planned_order_driver({'id': order.get('id')}))
        await message_menager.add_to_message_list(msg,  state, 'order_planned_messages')


async def pass_fun(message: types.Message, state: FSMContext) -> None:
    pass