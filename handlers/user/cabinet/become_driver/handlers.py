from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from handlers.common.helper import user_cabinet_menu
import json
from services.google_maps import find_city, find_region
from state.user import CreateDriver
from bot import bot
import os
from keyboards.default.users.become_driver import become_driver_kb
from utils.template_engine import render_template
from services.http_client import HttpDriver
from data.config import WEB_APP_ADDRESS
from handlers.common.helper import Handler, user_cabinet_menu

import texts


async def save_name(message: types.Message, state: FSMContext):
    full_name = message.text

    await state.update_data(full_name=full_name)

    await state.set_state(CreateDriver.waiting_region)
    await message.answer('Введіть область в якій ви будуте працювати 🌇')


async def save_region(message: types.Message, state: FSMContext):
    not_formatted_region = message.text
    region = await find_region(not_formatted_region)
    await state.update_data(region=region)

    await message.answer('Введіть місто в якому ви будуте працювати 🌇')
    await state.set_state(CreateDriver.waiting_city)


async def save_city(message: types.Message, state: FSMContext):
    not_formatted_city = message.text
    data = await state.get_data()
    region = data.get('region')
    city = await find_city(not_formatted_city, region)
    await state.update_data(city=city)

    await message.answer('Введіть марку та модель авто 🚗')
    await state.set_state(CreateDriver.waiting_car_name)


async def save_car_name(message: types.Message, state: FSMContext):
    car_name = message.text

    await state.update_data(car_name=car_name)

    await message.answer('Введіть номер вашого авто 🆔')
    await state.set_state(CreateDriver.waiting_car_number)


async def save_car_number(message: types.Message, state: FSMContext):
    car_number = message.text

    await state.update_data(car_number=car_number)

    await message.answer('Введіть кількість сидінь 💺')
    await state.set_state(CreateDriver.waiting_car_number_of_seats)


async def save_car_number_of_seats(message: types.Message, state: FSMContext):
    car_number_of_seats = message.text

    await state.update_data(car_number_of_seats=car_number_of_seats)

    await message.answer('Введіть колір авто 🟨')
    await state.set_state(CreateDriver.waiting_car_color)


async def save_car_color(message: types.Message, state: FSMContext):
    car_color = message.text

    await state.update_data(car_color=car_color)

    await message.answer('Надішліть фото водійського посвідчення 🪪')
    await message.answer('Водійське посвідчення із відкритою категорією "В" – стороною, де вказані Ваші фото, '
                         'ім`я та прізвище, номер документа та дата народження.')
    await state.set_state(CreateDriver.waiting_passport_photo)


async def save_passport_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()

    passport_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(passportPhoto=passport_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{passport_photo}")

    await message.answer('Надішліть фото техпаспорта 🪪')
    await message.answer('Cтороною, де вказаний державний номер авто та рік його випуску.')
    await state.set_state(CreateDriver.waiting_license_photo)


async def save_license_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()

    license_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(licensePhoto=license_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{license_photo}")

    await message.answer('Надішліть фото страховкі 🪪')
    await state.set_state(CreateDriver.waiting_insurance_photo)


async def save_insurance_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()

    insurance_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(insurancePhoto=insurance_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{insurance_photo}")

    await message.answer('Надішліть фото авто 🚗')
    await state.set_state(CreateDriver.waiting_car_photo)


async def save_car_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()

    car_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(carPhoto=car_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{car_photo}")

    template = render_template('become_driver.js2', data=data)
    await message.answer(template, reply_markup=become_driver_kb)
    await state.set_state(CreateDriver.waiting_accept)


async def confirm_request(message: types.Message, state: FSMContext):

    data = await state.get_data()
    temp_message = await message.answer(
        "Відправляємо дані..."
    )

    response = await HttpDriver.req_register_driver(data={
        "name": data.get('full_name'),
        "phone_number": data.get('phone_number'),
        "city": data.get('city'),
        "region": data.get('region'),
        "chat_id": message.chat.id,
        "status_id": 1,
        "car_name": data.get('car_name'),
        "car_number": data.get('car_number'),
        "car_number_of_seats": int(data.get('car_number_of_seats')),
        "car_color": data.get('car_color'),
        "comment": "тест",
        "rate": "5",
        "passport": f"{WEB_APP_ADDRESS}/media/{data.get('passportPhoto')}",
        "car": f"{WEB_APP_ADDRESS}/media/{data.get('carPhoto')}",
        "license": f"{WEB_APP_ADDRESS}/media/{data.get('licensePhoto')}",
        "insurance": f"{WEB_APP_ADDRESS}/media/{data.get('insurancePhoto')}",
        "type_id": 1
    })

    await temp_message.delete()

    if response.get('response_code') == 200:
        await message.answer('Заявку відпралено, очікуйте її пітвердження ✅')
        return await user_cabinet_menu(state, message=message)
    elif response.get('response_code') != 200:
        return await message.answer(text=texts.SERVER_ERROR)


async def to_menu(message: types.Message, state: FSMContext):
    await user_cabinet_menu(state, message=message)