import json
from typing import Any, Coroutine, Dict

import aiohttp
import requests

from data.config import API_URL, API_KEY


class HttpClient:

    @staticmethod
    async def post(data: Any, **kwargs) -> dict[str, int | Any]:
        full_url = f'{kwargs.get("service")}{kwargs.get("path")}'
        print(f'ENDPOINT: {full_url}')

        headers = {
            "Accept": "application/json",
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            if isinstance(data, aiohttp.FormData):
                print(data._fields)
                async with session.post(url=full_url, data=data) as resp:
                    response = await resp.json()
            else:
                async with session.post(url=full_url, data=data) as resp:
                    response = await resp.json()

            print(f'RESP RESULT: {response}')
            return {'response_data': response, 'response_code': resp.status}

    @staticmethod
    async def get(**kwargs) -> dict[str, int | Any]:
        full_url = f'{kwargs.get("service")}{kwargs.get("path")}'
        print(f'ENDPOINT: {full_url}')

        headers = {
            "Accept": "application/json",
        }

        # resource = requests.post(url=full_url, json=encoded_data, headers=headers)
        # print(resource.content)
        async with aiohttp.ClientSession(headers=headers) as session:
            print(headers)
            async with session.get(url=full_url) as resp:
                response = await resp.json()
                print(f'RESP RESULT: {response}')
                return {'response_data': response, 'response_code': resp.status}


class HttpUser(HttpClient):
    BASE_URL = f'{API_URL}/user'

    @staticmethod
    async def request(path: str, data: dict):
        return await HttpClient.post(data=data, service=HttpUser.BASE_URL, path=path)

    @staticmethod
    async def register_user(data: dict):
        return await HttpUser.request('/createUser', data)

    @staticmethod
    async def get_user_info(data: dict):
        return await HttpUser.request('/getUser', data)

    @staticmethod
    async def update_user(data: dict):
        return await HttpUser.request('/updateUser', data)

    @staticmethod
    async def rete_user(data: dict):
        return await HttpDriver.request('/insertRate', data)


class HttpDriver(HttpClient):
    BASE_URL = f'{API_URL}/driver'

    @staticmethod
    async def request(path: str, data: dict):
        return await HttpClient.post(data=data, service=HttpDriver.BASE_URL, path=path)

    @staticmethod
    async def request_get(path: str):
        return await HttpClient.get(service=HttpDriver.BASE_URL, path=path)

    @staticmethod
    async def req_register_driver(data: dict):
        return await HttpDriver.request('/createDriver', data)

    @staticmethod
    async def get_driver_info(data: dict):
        return await HttpDriver.request('/getDriver', data)

    @staticmethod
    async def get_active_drivers(data: dict):
        return await HttpDriver.request('/getActiveDriver', data)

    @staticmethod
    async def set_active_driver(data: dict):
        return await HttpDriver.request('/setActiveDriver', data)

    @staticmethod
    async def set_deactive_driver(data: dict):
        return await HttpDriver.request('/setDeactiveDriver', data)

    @staticmethod
    async def rete_driver(data: dict):
        return await HttpDriver.request('/insertRate', data)

    @staticmethod
    async def get_class_taxi():
        return await HttpDriver.request_get('/getCarType')

    @staticmethod
    async def update_driver(data: dict):
        return await HttpDriver.request('/updateDriver', data)

    @staticmethod
    async def insert_driver_balance(data: dict):
        return await HttpDriver.request('/insertBalance', data)


class HttpOrder(HttpClient):
    BASE_URL = f'{API_URL}/order'

    @staticmethod
    async def request(path: str, data: dict):
        return await HttpClient.post(data=data, service=HttpOrder.BASE_URL, path=path)

    @staticmethod
    async def request_get(path: str):
        return await HttpClient.get(service=HttpOrder.BASE_URL, path=path)

    @staticmethod
    async def create_order(data):
        return await HttpOrder.request('/createOrder', data)

    @staticmethod
    async def update_order(data: dict):
        return await HttpOrder.request('/updateOrder', data)

    @staticmethod
    async def get_order(data: dict):
        return await HttpOrder.request('/getOrder', data)

    @staticmethod
    async def get_user_order(data: dict):
        return await HttpOrder.request('/getUserOrder', data)

    @staticmethod
    async def get_driver_order(data: dict):
        return await HttpOrder.request('/getDriverOrder', data)

    @staticmethod
    async def get_order_price(data: dict):
        data = {
            'feed_distance[0]': 0.1,
            'trip_distance[0]': data.get('kilometers'),
            'distance_from_end_point_to_point': 0.1,
            'number_idle_minutes[0]': 1,
            'car_type_id': data.get('car_type_id')
        }
        return await HttpOrder.request('/cost_calculation', data)

    @staticmethod
    async def accept_order(data: dict):
        return await HttpOrder.request('/acceptOrder', data)

    @staticmethod
    async def complete_order(data: dict):
        return await HttpOrder.request('/completeOrder', data)

    @staticmethod
    async def cancel_order(data: dict):
        return await HttpOrder.request('/deleteOrder', data)

    @staticmethod
    async def get_additional_services():
        return await HttpOrder.request_get('/additional_services')


class HttpOther(HttpClient):

    @staticmethod
    async def get_status_online_payment():
        return await HttpClient.get(service=f'{API_URL}/online_payment', path='/online_payment')

    @staticmethod
    async def get_text_greeting():
        return await HttpClient.get(service=f'{API_URL}/title', path='/title')