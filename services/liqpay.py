from liqpay import LiqPay
import pyshorteners
import json
import httpx
from data.config import LIQPAY_PRIVATE_KEY, LIQPAY_PUBLIC_KEY, WEB_APP_ADDRESS, BOT_URL

liqpay = LiqPay(LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY)
shortener = pyshorteners.Shortener()


async def create_payment(cost, order_id):
    params = {
        'action': 'hold',
        'amount': cost,
        'currency': 'UAH',
        'description': 'Оплата за таксі',
        'order_id': int(order_id),
        'version': '3',
        'sandbox': '1', 
        'server_url': f'{WEB_APP_ADDRESS}/callback',
        'result_url': BOT_URL,
    }

    signature = liqpay.cnb_signature(params)
    
    data = liqpay.cnb_data(params)
    url = f'https://www.liqpay.ua/api/3/checkout?data={data}&signature={signature}'
    short_url = shortener.tinyurl.short(url)
    
    return short_url


async def payment_completion(order_id):
    params = {
        "action": "hold_completion",
        "version": "3",
        "sandbox": '1',
        "order_id": int(order_id)
    }
    signature = liqpay.cnb_signature(params)
    data = liqpay.cnb_data(params)
    async with httpx.AsyncClient(verify=True) as client:
        response = await client.post('https://www.liqpay.ua/api/request', data={'data': data, 'signature': signature})
        return response.json()

async def refund_payment(order_id):
    params = {
        "action": "refund",
        "version": "3",
        "sandbox": '1',
        "order_id": int(order_id)
    }
    signature = liqpay.cnb_signature(params)
    data = liqpay.cnb_data(params)
    async with httpx.AsyncClient(verify=True) as client:
        response = await client.post('https://www.liqpay.ua/api/request', data={'data': data, 'signature': signature})
        return response.json()