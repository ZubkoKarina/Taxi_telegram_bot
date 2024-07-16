from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import json

from handlers.common.helper import user_cabinet_menu
from services.http_client import HttpUser
from keyboards.default.users.setting import edit_user
from state.user import EditUserInfo
from utils.template_engine import render_template
from aiogram.types import ReplyKeyboardRemove

import texts


async def edit_name(message: types.Message, state: FSMContext):
    await message.answer(texts.ASKING_NAME, reply_markup=ReplyKeyboardRemove())

    await state.set_state(EditUserInfo.waiting_name)


async def edit_city(message: types.Message, state: FSMContext):
    await message.answer(texts.ASKING_CITY, reply_markup=ReplyKeyboardRemove())

    await state.set_state(EditUserInfo.waiting_city)


async def confirm_city(message: types.Message, state: FSMContext):
    city = message.text
    chat_id = message.chat.id

    response = await HttpUser.update_user(data={
        'chat_id': chat_id,
        'city': city,
    })

    if response.get('response_code') != 200:
        return message.answer(texts.SERVER_ERROR)
    await message.answer(texts.ASKING_EDIT_CITY)
    await state.update_data(city=city)
    print(await state.get_data())

    await open_setting_menu(message, state)


async def confirm_name(message: types.Message, state: FSMContext):
    name = message.text
    chat_id = message.chat.id

    response = await HttpUser.update_user(data={
        'chat_id': chat_id,
        'name': name,
    })

    if response.get('response_code') != 200:
        return message.answer(texts.SERVER_ERROR)
    await message.answer(texts.ASKING_EDIT_NAME)
    await state.update_data(name=name)

    await open_setting_menu(message, state)


async def open_setting_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    template = render_template("user_info.js2", data=data)
    await message.answer(text=template, reply_markup=edit_user)

    await state.set_state(EditUserInfo.waiting_edit_info)


async def open_menu(message: types.Message, state: FSMContext):
    await user_cabinet_menu(state, message=message)
