from typing import NamedTuple, Callable, Optional
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from texts import TextManager, get_text_manager
from state.user import UserCabinetStates
from state.driver import DriverCabinetStates
from keyboards import KeyboardManager, get_kb_manager
from utils.template_engine import render_template
from services.redis import RedisClient
from services.http_client import HttpDriver
from aiogram.fsm.context import FSMContext, StorageKey
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from bot import dp, bot
import json


class Handler(NamedTuple):
    handler: Callable
    filters: list


class CallbackDataContainsKey(BaseFilter):
    def __init__(self, key: str):
        self.key = key

    async def __call__(self, callback_query: types.CallbackQuery) -> bool:
        try:
            data = callback_query.data
            data_dict = json.loads(data)
            if self.key in data_dict:
                return self.key in data_dict
            else:
                return False
        except (IndexError, json.JSONDecodeError):
            return False


async def user_cabinet_menu(state: FSMContext, **kwargs: object) -> object:
    await state.set_state(UserCabinetStates.waiting_menu)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    print(f'USER DATA: {await state.get_data()}')

    return await independent_message(
        msg_text=user_text_manager.asking.MENU, reply_markup=user_kb_manager.default.users.menu, **kwargs
    )


async def driver_cabinet_menu(state: FSMContext, **kwargs: object) -> object:
    await state.set_state(DriverCabinetStates.waiting_menu)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    menu_kb = user_kb_manager.default.driver.menu
    if data.get('status').get('id') == 2:
        menu_kb = user_kb_manager.default.driver.inactive_menu

    print(f'DRIVER DATA: {data}')
    template = render_template("authorization_driver.js2", data=data, lang_code=data.get('user_language'))

    return await independent_message(
        msg_text=template, reply_markup=menu_kb, **kwargs
    )


async def independent_message(msg_text: str, reply_markup: Optional = None, **kwargs):
    message: types.Message = kwargs.get("message")

    if message:
        return await message.answer(text=msg_text, reply_markup=reply_markup)
    else:
        bot: Bot = kwargs.get("bot")
        chat_id: int = kwargs.get("chat_id")

        return await bot.send_message(chat_id=chat_id, text=msg_text, reply_markup=reply_markup)


async def get_drivers(region: str):
    resp = await HttpDriver.get_active_drivers(data={'region': region})
    drivers_resp = resp.get('response_data').get('data')
    drivers = []

    for driver in drivers_resp:
        chat_id = driver.get('chat_id')
        resp = await HttpDriver.get_driver_info(data={'chat_id': chat_id})
        driver_data = resp.get('response_data').get('data')
        name = driver_data.get('name')
        car = driver_data.get('car')

        driver_state: FSMContext = FSMContext(dp.storage, StorageKey(chat_id=chat_id, user_id=chat_id, bot_id=bot.id))
        driver_state_data = await driver_state.get_data()
        geo = driver_state_data.get("geo")
        lang_code = driver_state_data.get('lang_code')

        driver_info = {
            'chat_id': chat_id,
            'name': name,
            'car': car,
            'geo': geo,
            'lang_code': lang_code,
        }
        drivers.append(driver_info)

    return drivers


async def mass_notification_deletion(list_chat_id, list_msg_id):
    for chat_id in list_chat_id:
        for msg_id in list_msg_id:
            try:
                await bot.delete_message(chat_id, msg_id)
            except Exception as ex:
                pass
    return
