from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import asyncio
import texts
from state.driver import DriverCabinetStates
from services.http_client import HttpDriver
from handlers.common.helper import driver_cabinet_menu

from keyboards.default.driver.menu import driver_menu_kb, driver_menu_text


async def main_handlers(message: types.Message, state: FSMContext):
    bt_text = message.text

    if bt_text == driver_menu_text['activate']:
        await message.answer(texts.ASKING_SHARE_GEO)
        await state.set_state(DriverCabinetStates.waiting_geo)
    if bt_text == driver_menu_text['deactivate']:
        await state.update_data(status='Неактивний')
        await HttpDriver.set_active_driver(data={
            'chat_id': message.chat.id
        })
        await message.answer('Ви зійшли з лінії')
        await driver_cabinet_menu(state, message=message)


async def access_to_line(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    await state.update_data(status='Активний')
    await HttpDriver.set_active_driver(data={
        'chat_id': message.chat.id
    })
    await state.update_data(geo=[lat, lon])

    await message.answer(texts.GOT_ON_LINE)
    await message.answer('Чекайте замовлення або можите переглянути які є замовлення у вашому місті 🌇',
                         reply_markup=driver_menu_kb)

    await state.set_state(DriverCabinetStates.waiting_menu)


async def tracking_location(message: types.Message, state: FSMContext):

    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(geo=[lat, lon])
    print(f"місцезнаходження змінено: широта={lat}, довгота={lon}")

