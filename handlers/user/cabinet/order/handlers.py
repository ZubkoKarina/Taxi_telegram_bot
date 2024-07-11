from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
import json

from handlers.common.helper import get_drivers, user_cabinet_menu
from keyboards.inline.order import open_web_app_order_kb
from utils.distance_calculation import haversine
from services.http_client import HttpOrder, HttpUser
from state.user import OrderTaxi
from aiogram.types import ReplyKeyboardRemove
from bot import bot
import texts
from texts.keyboards import OPEN_MENU


async def ask_city(message: types.Message, state: FSMContext):
    await message.answer(text=texts.ASKING_CITY, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderTaxi.waiting_new_city)


async def edit_city(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(City=city)
    data = await state.get_data()

    await ask_open_order(message, state)


async def ask_open_order(message: types.Message, state: FSMContext):
    await message.answer(text='Для початку оформлення таксі нажміть кнопку нище 👇',
                         reply_markup=open_web_app_order_kb)

    await state.set_state(OrderTaxi.waiting_order_data)


async def accept_order_data(message: types.Message, state: FSMContext):
    data = message.web_app_data.data
    try:
        data_dict = json.loads(data)

        from_address = data_dict.get('addressFrom')
        to_address = data_dict.get('addressTo')
        taxi_class = data_dict.get('taxiClass')
        pay_method = data_dict.get('payMethod')
        from_coordinates = data_dict.get('fromCoordinates')
        to_coordinates = data_dict.get('toCoordinates')

        response_message = (
            f"Замовлення отримано✅"
            f"Звідки: {from_address}\n"
            f"Куди: {to_address}\n"
            f"Клас таксі: {taxi_class}\n"
            f"Метод оплати: {pay_method}"
        )

        await message.answer(response_message)

        order = {
            'from_address': from_address,
            'to_address': to_address,
            'taxi_class': taxi_class,
            'pay_method': pay_method,
            'from_coordinates': from_coordinates,
            'to_coordinates': to_coordinates
        }

        # await HttpOrder.create_order(data={
        #     'shipping_address': from_address,
        #     'arrival_address': to_address,
        #     'payment_method': pay_method,
        #     'comment': '',
        #     'user_chat_id': '',
        # })

        print(order)
        await state.update_data(order=order)
        await search_drivers(message, state)

    except json.JSONDecodeError:
        print('Помилка обробки замовлення. Невірний формат даних.')


async def search_drivers(message: types.Message, state: FSMContext):
    drivers = await get_drivers()
    passenger_data = await state.get_data()
    order_data = passenger_data.get('order')

    for driver in drivers:
        geo_driver = driver.get('geo')
        from_geo = order_data.get('from_coordinates')
        distance_driver = haversine(from_geo, geo_driver)
        print(distance_driver)
        if distance_driver <= 10:
            driver_chat_id = driver.get('chat_id')
            await bot.send_message(driver_chat_id, f'Замволення на суму - 0.0 грн\n'
                                                   f'Звідки: {order_data.get("from_address")}\n'
                                                   f'Куди: {order_data.get("to_address")}\n'
                                                   f'Метод оплати: {order_data.get("pay_method")}'
                                   )
