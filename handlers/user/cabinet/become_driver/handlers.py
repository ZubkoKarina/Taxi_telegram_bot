from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from handlers.common.helper import user_cabinet_menu
import json
from services.google_maps import find_city, find_region
from state.user import CreateDriver
from bot import bot
import os
from utils.template_engine import render_template
from services.http_client import HttpDriver
from data.config import WEB_APP_ADDRESS
from handlers.common.helper import Handler, user_cabinet_menu
from keyboards import KeyboardManager, get_kb_manager
from texts import TextManager, get_text_manager
from services.visicom import search_settlement


async def save_name(message: types.Message, state: FSMContext):
    full_name = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await state.update_data(full_name=full_name)

    await state.set_state(CreateDriver.waiting_region)
    await message.answer(user_text_manager.asking.ENTER_WORK_REGION)


async def save_region(message: types.Message, state: FSMContext):
    not_formatted_region = message.text
    region = await find_region(not_formatted_region)
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    if region is None:
        await message.answer(user_text_manager.asking.REGION_NOT_FOUND)
        await message.answer(user_text_manager.asking.REGION)
        return
    await state.update_data(region=region)

    await message.answer(user_text_manager.asking.ENTER_WORK_CITY)
    await state.set_state(CreateDriver.waiting_city)


async def save_city(message: types.Message, state: FSMContext):
    not_formatted_city = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    region = data.get('region')
    city = search_settlement(not_formatted_city, region)
    if city == 'DUPLICATE':
        return message.answer(user_text_manager.asking.DUPLICATE_SETTLEMENT)

    if city is None:
        await message.answer(user_text_manager.asking.CITY_NOT_FOUND)
        await message.answer(user_text_manager.asking.CITY)
        return
    await state.update_data(city=city)

    await message.answer(user_text_manager.asking.ENTER_CAR_MODEL)
    await state.set_state(CreateDriver.waiting_car_name)


async def save_car_name(message: types.Message, state: FSMContext):
    car_name = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await state.update_data(car_name=car_name)

    await message.answer(user_text_manager.asking.ENTER_CAR_NUMBER)
    await state.set_state(CreateDriver.waiting_car_number)


async def save_car_number(message: types.Message, state: FSMContext):
    car_number = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await state.update_data(car_number=car_number)

    await message.answer(user_text_manager.asking.ENTER_SEAT_COUNT)
    await state.set_state(CreateDriver.waiting_car_number_of_seats)


async def save_car_number_of_seats(message: types.Message, state: FSMContext):
    car_number_of_seats = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await state.update_data(car_number_of_seats=car_number_of_seats)

    await message.answer(user_text_manager.asking.ENTER_CAR_COLOR)
    await state.set_state(CreateDriver.waiting_car_color)


async def save_car_color(message: types.Message, state: FSMContext):
    car_color = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await state.update_data(car_color=car_color)

    await message.answer(user_text_manager.asking.SEND_CAR_FRONT_PASSPORT_PHOTO)
    await message.answer(user_text_manager.asking.CAR_PASSPORT_DETAILS)
    await state.set_state(CreateDriver.waiting_front_passport_photo)


async def save_front_passport_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    front_passport_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(frontPassportPhoto=front_passport_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{front_passport_photo}")

    await message.answer(user_text_manager.asking.SEND_CAR_BACK_PASSPORT_PHOTO)
    await state.set_state(CreateDriver.waiting_back_passport_photo)


async def save_back_passport_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    back_passport_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(backPassportPhoto=back_passport_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{back_passport_photo}")

    await message.answer(user_text_manager.asking.SEND_DRIVER_LICENSE_PHOTO)
    await message.answer(user_text_manager.asking.DRIVER_LICENSE_DETAILS)
    await state.set_state(CreateDriver.waiting_license_photo)


async def save_license_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    license_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(licensePhoto=license_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{license_photo}")

    await message.answer(user_text_manager.asking.SEND_INSURANCE_PHOTO)
    await state.set_state(CreateDriver.waiting_insurance_photo)


async def save_insurance_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    insurance_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(insurancePhoto=insurance_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{insurance_photo}")

    await message.answer(user_text_manager.asking.SEND_FRONT_CAR_PHOTO)
    await state.set_state(CreateDriver.waiting_front_car_photo)


# async def save_car_photo(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     user_text_manager: TextManager = get_text_manager(data.get('user_language'))
#     user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
#
#     car_photo = f"{message.photo[-1].file_id}.jpg"
#
#     await state.update_data(carPhoto=car_photo)
#
#     await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{car_photo}")
#
#     await message.answer(user_text_manager.asking.SEND_FRONT_CAR_PHOTO)
#     await state.set_state(CreateDriver.waiting_front_car_photo)


async def save_front_car_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    front_car_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(frontCarPhoto=front_car_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{front_car_photo}")

    await message.answer(user_text_manager.asking.SEND_BACK_CAR_PHOTO)
    await state.set_state(CreateDriver.waiting_back_car_photo)


async def save_back_car_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    back_car_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(backCarPhoto=back_car_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{back_car_photo}")

    await message.answer(user_text_manager.asking.SEND_LEFT_CAR_PHOTO)
    await state.set_state(CreateDriver.waiting_left_car_photo)


async def save_left_car_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    left_car_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(leftCarPhoto=left_car_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{left_car_photo}")

    await message.answer(user_text_manager.asking.SEND_RIGHT_CAR_PHOTO)
    await state.set_state(CreateDriver.waiting_right_car_photo)


async def save_right_car_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    right_car_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(rightCarPhoto=right_car_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{right_car_photo}")

    await message.answer(user_text_manager.asking.SEND_FRONT_ROW_CAR_PHOTO)
    await state.set_state(CreateDriver.waiting_front_row_car_photo)


async def save_front_row_car_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    front_row_car_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(frontRowCarPhoto=front_row_car_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{front_row_car_photo}")

    await message.answer(user_text_manager.asking.SEND_BACK_ROW_CAR_PHOTO)
    await state.set_state(CreateDriver.waiting_back_row_car_photo)


async def save_back_row_car_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    back_row_car_photo = f"{message.photo[-1].file_id}.jpg"

    await state.update_data(backRowCarPhoto=back_row_car_photo)

    await bot.download(message.photo[-1], destination=f"{os.getcwd()}/media/{back_row_car_photo}")

    await message.answer(user_text_manager.asking.SEND_COMMENT, reply_markup=user_kb_manager.default.skip)
    await state.set_state(CreateDriver.waiting_comment)


async def skip_comment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    template = render_template('become_driver.js2', data=data, lang_code=data.get('user_language'))
    await message.answer(template, reply_markup=user_kb_manager.default.users.become_driver)
    await state.set_state(CreateDriver.waiting_accept)


async def save_comment(message: types.Message, state: FSMContext):
    comment = message.text
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))

    await state.update_data(comment=comment)

    template = render_template('become_driver.js2', data=data, lang_code=data.get('user_language'))
    await message.answer(template, reply_markup=user_kb_manager.default.users.become_driver)
    await state.set_state(CreateDriver.waiting_accept)


async def confirm_request(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_text_manager: TextManager = get_text_manager(data.get('user_language'))
    user_kb_manager: KeyboardManager = get_kb_manager(data.get('user_language'))
    temp_message = await message.answer(
        user_text_manager.services.SEND_DATA
    )

    response = await HttpDriver.req_register_driver(data={
        "name": data.get('full_name'),
        "phone_number": data.get('phone_number'),
        "city": data.get('city'),
        "region": data.get('region'),
        "chat_id": message.chat.id,
        "status_id": 2,
        "car_name": data.get('car_name'),
        "car_number": data.get('car_number'),
        "car_number_of_seats": int(data.get('car_number_of_seats')),
        "car_color": data.get('car_color'),
        "comment": data.get('comment'),
        "rate": "5",
        "passport_1": f"{WEB_APP_ADDRESS}/media/{data.get('frontPassportPhoto')}",
        "passport_2": f"{WEB_APP_ADDRESS}/media/{data.get('backPassportPhoto')}",
        "license": f"{WEB_APP_ADDRESS}/media/{data.get('licensePhoto')}",
        "insurance": f"{WEB_APP_ADDRESS}/media/{data.get('insurancePhoto')}",
        "front_photo": f"{WEB_APP_ADDRESS}/media/{data.get('frontCarPhoto')}",
        "left_photo": f"{WEB_APP_ADDRESS}/media/{data.get('leftCarPhoto')}",
        "right_photo": f"{WEB_APP_ADDRESS}/media/{data.get('rightCarPhoto')}",
        "back_photo": f"{WEB_APP_ADDRESS}/media/{data.get('backCarPhoto')}",
        "front_row_photo": f"{WEB_APP_ADDRESS}/media/{data.get('frontRowCarPhoto')}",
        "back_row_photo": f"{WEB_APP_ADDRESS}/media/{data.get('backRowCarPhoto')}",
        "type_id": 1
    })

    await temp_message.delete()

    if response.get('response_code') == 200:
        await message.answer(user_text_manager.asking.SUBMISSION_SUCCESS)
        return await user_cabinet_menu(state, message=message)
    elif response.get('response_code') != 200:
        return await message.answer(text=user_text_manager.services.SERVER_ERROR)


async def to_menu(message: types.Message, state: FSMContext):
    await user_cabinet_menu(state, message=message)
