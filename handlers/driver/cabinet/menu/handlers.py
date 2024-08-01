from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import asyncio
import texts
from state.driver import DriverCabinetStates, EditDriver
from services.http_client import HttpDriver, HttpOrder
from handlers.common.helper import driver_cabinet_menu
from bot import bot
from utils.template_engine import render_template
from handlers.common.inline_mode import InlineHandlers
from keyboards.inline.history_order import choose_order

from keyboards.default.driver.menu import driver_menu_kb, driver_menu_text
from keyboards.default.driver.setting import edit_driver_kb


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text
    data = await state.get_data()

    if bt_text == driver_menu_text['activate']:
        await message.answer(texts.ASKING_SHARE_GEO)
        await state.set_state(DriverCabinetStates.waiting_geo)
    if bt_text == driver_menu_text['deactivate']:
        await quit_to_line(message, state)
    if bt_text == driver_menu_text['info']:
        await driver_info(message, state)
    if bt_text == driver_menu_text['setting']:
        template = render_template("user_info.js2", data=data)
        await message.answer(text=template, reply_markup=edit_driver_kb)
        await state.set_state(EditDriver.waiting_edit_menu)
    elif bt_text == driver_menu_text['history_order']:
        await state.update_data(chat_id=message.chat.id)
        await message.answer(text='Тут ви сможите переглаянути історію ваших поїздок та їх деталі', reply_markup=ReplyKeyboardRemove())
        await message.answer(text='Оберіть зі списку ваше замоленя 👇', reply_markup=choose_order)
        await state.set_state(DriverCabinetStates.waiting_history_order)


async def quit_to_line(message: types.Message, state: FSMContext):
    data = await state.get_data()
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
    await state.set_data(driver_data)
    await message.answer('Ви зійшли з лінії')

    await driver_cabinet_menu(state, message=message)


async def access_to_line(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    if message.location.live_period is None:
        return await message.answer(texts.ASKING_INCORRECT_GEO_PROVISION)
    if message.location.live_period <= 28800:
        return await message.answer(texts.ASKING_INCORRECT_TIME_GEO)

    response = await HttpDriver.set_active_driver(data={
        'chat_id': message.chat.id
    })
    driver_data = response.get('response_data').get('data')
    if response.get('response_code') != 200 or driver_data.get('is_banned'):
        await driver_cabinet_menu(state, message=message)
        return
    await state.set_data(driver_data)
    await state.update_data(geo=[lat, lon], msg_id_geo=message.message_id)

    await message.answer(texts.GOT_ON_LINE)
    await message.answer('Чекайте замовлення або можите переглянути які є замовлення у вашому місті 🌇',
                         reply_markup=driver_menu_kb)

    await state.set_state(DriverCabinetStates.waiting_menu)


async def tracking_location(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_id_geo = data.get('msg_id_geo')

    if message.message_id != msg_id_geo:
        return
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(geo=[lat, lon])
    print(f"місцезнаходження змінено: широта={lat}, довгота={lon}")


async def driver_info(message: types.Message, state: FSMContext):
    data = await state.get_data()

    template = render_template("driver_info.js2", data=data)

    await message.answer(template)


async def show_history_order(callback: types.InlineQuery, state: FSMContext):
    user_data = await state.get_data()
    response = await HttpOrder.get_driver_order(data={'chat_id': user_data.get('chat_id')})
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
