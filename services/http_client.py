import json
from typing import Any, Coroutine, Dict

import aiohttp
import requests

from data.config import API_URL, API_KEY


class HttpClient:

    @staticmethod
    async def post(data: dict, **kwargs) -> dict[str, int | Any]:
        encoded_data = json.dumps(data)

        full_url = f'{kwargs.get("service")}{kwargs.get("path")}'
        print(f'ENDPOINT: {full_url}')

        headers = {
            "Accept": "application/json",
        }

        # resource = requests.post(url=full_url, json=encoded_data, headers=headers)
        # print(resource.content)
        async with aiohttp.ClientSession(headers=headers) as session:
            print(headers)
            print(f'DATA: {encoded_data}')
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
    async def get_active_drivers():
        return await HttpDriver.request_get('/getActiveDriver')

    @staticmethod
    async def set_active_driver(data: dict):
        return await HttpDriver.request('/setActiveDriver', data)

    @staticmethod
    async def set_deactive_driver(data: dict):
        return await HttpDriver.request('/setActiveDriver', data)


class HttpOrder(HttpClient):
    BASE_URL = f'{API_URL}/order'

    @staticmethod
    async def request(path: str, data: dict):
        return await HttpClient.post(data=data, service=HttpOrder.BASE_URL, path=path)

    @staticmethod
    async def create_order(data: dict):
        return await HttpOrder.request('/createOrder', data)

    @staticmethod
    async def get_user_order(data: dict):
        return await HttpOrder.request('/getUserOrder', data)

    @staticmethod
    async def get_user_driver(data: dict):
        return await HttpOrder.request('/getDriverOrder', data)