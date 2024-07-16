from typing import NamedTuple, Callable, Optional
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

import texts
from state.user import UserCabinetStates
from state.driver import DriverCabinetStates
from keyboards.default.users.menu import user_menu_kb
from keyboards.default.driver.menu import driver_menu_kb, inactive_driver_menu_kb
from utils.template_engine import render_template
from services.redis import RedisClient
from services.http_client import HttpDriver
import json


class Handler(NamedTuple):
    handler: Callable
    filters: list


async def user_cabinet_menu(state: FSMContext, **kwargs: object) -> object:
    await state.set_state(UserCabinetStates.waiting_menu)

    print(f'USER DATA: {await state.get_data()}')

    return await independent_message(
        text=texts.ASKING_MENU, reply_markup=user_menu_kb, **kwargs
    )


async def driver_cabinet_menu(state: FSMContext, **kwargs: object) -> object:
    await state.set_state(DriverCabinetStates.waiting_menu)
    data = await state.get_data()

    menu_kb = driver_menu_kb
    if data.get('status').get('id') == 2 or data.get('status') == 'Неактивний':
        menu_kb = inactive_driver_menu_kb

    print(f'DRIVER DATA: {data}')
    template = render_template("authorization_driver.js2", data=data)

    return await independent_message(
        text=template, reply_markup=menu_kb, **kwargs
    )


async def independent_message(text: str, reply_markup: Optional = None, **kwargs):
    message: types.Message = kwargs.get("message")

    if message:
        return await message.answer(text=text, reply_markup=reply_markup)
    else:
        bot: Bot = kwargs.get("bot")
        chat_id: int = kwargs.get("chat_id")

        return await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


async def get_drivers():
    resp = await HttpDriver.get_active_drivers()
    drivers_data = resp.get('response_data').get('data')
    drivers = []
    redis_cli = RedisClient()
    all_states = redis_cli.get_all_states()

    for driver in drivers_data:
        chat_id = driver.get('user').get('chat_id')
        name = driver.get('name')
        car = driver.get('car')
        status = driver.get('status').get('id')

        for state, state_value in all_states.items():
            type_state = state.split(':')[-1]
            state_chat_id = state.split(':')[-3]
            if type_state == 'data' and state_chat_id == chat_id and status == 1:
                print(state_value)
                try:
                    state_data = json.loads(state_value)
                    geo = state_data.get("geo")
                    driver_info = {
                        'chat_id': chat_id,
                        'name': name,
                        'car': car,
                        'geo': geo,
                    }
                    drivers.append(driver_info)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON for state: {state}")
    print(drivers)
    return drivers
