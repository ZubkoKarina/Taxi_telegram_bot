from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import os
from services.http_client import HttpUser, HttpOrder, HttpDriver
from handlers.user.cabinet.order.handlers import create_order, accept_order
from services.liqpay import liqpay
from data.config import LIQPAY_PRIVATE_KEY, LIQPAY_PUBLIC_KEY

web_app = FastAPI()

static_dir = os.path.join(os.path.dirname(__file__), "static")

if not os.path.isdir(static_dir):
    raise RuntimeError(f"Directory '{static_dir}' does not exist")

web_app.mount("/static", StaticFiles(directory='web_app/static'), name="static")
web_app.mount("/media", StaticFiles(directory='media'), name="media")
templates = Jinja2Templates(directory='web_app/templates')


@web_app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@web_app.get('/get-taxi-class')
async def get_api_key():
    response = await HttpDriver.get_class_taxi()
    return response.get('response_data').get('data')


@web_app.get('/get-user-city')
async def get_api_key(chat_id: int):
    response = await HttpUser.get_user_info(data={
        'chat_id': chat_id
    })
    user_data = response.get('response_data').get('data')
    print(f'USER {chat_id}: {user_data.get("city")}')
    return user_data.get('city')


@web_app.get('/get-order-price')
async def get_order_price(distance: int, duration: int, taxi_class):
    taxi_class = int(taxi_class)
    distance = distance / 1000
    duration = duration / 60

    response = await HttpOrder.get_order_price(data={
        "kilometers": distance,
        "is_city": 1,
        "is_route_made_by_air": 0,
        "time": duration,
        "car_type_id": taxi_class
    })

    price_data = response.get('response_data').get('data')
    return price_data.get('cost')


@web_app.post("/send_order_data")
async def send_order_data(request: Request):
    order_data = await request.json()
    await create_order(order_data)
    return JSONResponse(content={"message": "Order data received successfully"})

@web_app.post("/callback")
async def liqpay_callback(request: Request):
    form = await request.form()
    data = form['data']
    signature = form['signature']
    print(1111111111111111)
    expected_signature = liqpay.str_to_sign(LIQPAY_PRIVATE_KEY + data + LIQPAY_PRIVATE_KEY)
    if expected_signature == signature:
        decoded_data = liqpay.decode_data_from_str(data)
        print(decoded_data)
        if decoded_data['status'] == 'success' or decoded_data['status'] == 'sandbox':
            print(33333333333333)
            await accept_order(decoded_data['order_id'])
            return JSONResponse(content={"status": "success"})
    return JSONResponse(content={"status": "failure"})



@web_app.get('/log')
async def get_api_key(message: str):
    print(f"INFO: {message}")

