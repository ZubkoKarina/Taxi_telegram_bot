from aiogram import types, Bot
from aiogram.fsm.context import FSMContext, StorageKey
import json
import asyncio

from handlers.common.helper import get_drivers, user_cabinet_menu, mass_notification_deletion, driver_cabinet_menu
from services.google_maps import geocode_place_by_name
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser, HttpDriver
from state.user import OrderTaxi
from services.liqpay import create_payment, refund_payment
from aiogram.types import ReplyKeyboardRemove
from bot import bot
from texts import TextManager, get_text_manager
from utils.template_engine import render_template
from handlers.user.cabinet.common import open_menu
from bot import dp
from services.visicom import get_place
import time
from keyboards import KeyboardManager, get_kb_manager


async def accept_driver_application(chat_id):
    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    msg = await bot.send_message(chat_id=chat_id, text=user_text_manager.asking.ACCEPT_DRIVER_APPLICATION)

    user_language = data.get('user_language')
    response = await HttpDriver.get_driver_info({'chat_id': msg.chat.id})
    user_data = response.get('response_data').get('data')
    if response.get('response_code') == 200 and not user_data.get('is_banned'):
        await state.set_data({**user_data, 'user_language': user_language})

        await driver_cabinet_menu(state, message=msg)
        return

async def cancel_driver_application(chat_id, comment: str):
    state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))

    await bot.send_message(chat_id=chat_id, text=user_text_manager.asking.CANCEL_DRIVER_APPLICATION)
    if comment is not None:
        await bot.send_message(chat_id=chat_id, text=user_text_manager.asking.comment)
    return



