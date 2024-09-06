from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import os
from services.http_client import HttpUser, HttpOrder, HttpDriver, HttpOther
from handlers.user.cabinet.order.handlers import create_order, accept_order
from handlers.common import push_notification
from services.liqpay import liqpay
from data.config import LIQPAY_PRIVATE_KEY, LIQPAY_PUBLIC_KEY
from services import visicom

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


@web_app.post('/search_places')
async def search_places(data: Request):
    categories_exclude = 'adm_country,adm_district,adm_level1,adm_place,adm_settlement,hst_district,roa_road'

    data = await data.json()

    print(data.get('query'), data.get('city_id'))
    result_autocomplete = visicom.autocomplete(query=data.get('query'), near_place_id=data.get('city_id'),
                                               categories_exclude=categories_exclude)
    address_list = visicom.visicom_address_constructor(result_autocomplete)

    print(address_list)
    return address_list


@web_app.post('/get_place')
async def get_place(data: Request):
    data = await data.json()

    place = visicom.get_place(data.get('query'))

    return place


@web_app.post('/get_address_numbers')
async def get_address_numbers(data: Request):
    data = await data.json()

    address_list = visicom.get_address_numbers(data.get('street_id'))

    return address_list


@web_app.post('/get_place_geo')
async def get_place_geo(data: Request):
    data = await data.json()

    geo = visicom.get_place_geo(data.get('place_id'))
    geo = {'lat': geo[1], 'lng': geo[0]}

    return geo


@web_app.post('/get_place_by_geo')
async def get_place_geo(data: Request):
    data = await data.json()

    place = visicom.get_place_by_geo(data.get('lat'), data.get('lng'))

    return place


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


@web_app.get('/additional_services')
async def get_additional_services():
    response = await HttpOrder.get_additional_services()
    return response.get('response_data').get('data')


@web_app.get('/online_payment')
async def get_status_online_payment():
    response = await HttpOther.get_status_online_payment()
    print(response.get('response_data').get('data'))
    return response.get('response_data').get('data').get('is_active')


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
    expected_signature = liqpay.str_to_sign(LIQPAY_PRIVATE_KEY + data + LIQPAY_PRIVATE_KEY)
    if expected_signature == signature:
        decoded_data = liqpay.decode_data_from_str(data)
        print(decoded_data)
        if decoded_data['status'] == 'success' or decoded_data['status'] == 'sandbox':
            await accept_order(decoded_data['order_id'])
            return JSONResponse(content={"status": "success"})
    return JSONResponse(content={"status": "failure"})


@web_app.get('/log')
async def get_api_key(message: str):
    print(f"INFO: {message}")


@web_app.post('/accept_driver_application')
async def accept_driver_application_notification(data: Request):
    data = await data.json()

    await push_notification.accept_driver_application(data.get('chat_id'))

