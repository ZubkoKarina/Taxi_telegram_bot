from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import asyncio
import texts
from state.driver import DriverCabinetStates
from services.http_client import HttpDriver
from handlers.common.helper import driver_cabinet_menu
from bot import bot

from keyboards.default.driver.menu import driver_menu_kb, driver_menu_text


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text

    if bt_text == driver_menu_text['activate']:
        await message.answer(texts.ASKING_SHARE_GEO)
        await state.set_state(DriverCabinetStates.waiting_geo)
    if bt_text == driver_menu_text['deactivate']:
        await quit_to_line(message, state)


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
