from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import os
from services.http_client import HttpUser, HttpOrder

web_app = FastAPI()

static_dir = os.path.join(os.path.dirname(__file__), "static")

if not os.path.isdir(static_dir):
    raise RuntimeError(f"Directory '{static_dir}' does not exist")

web_app.mount("/static", StaticFiles(directory='web_app/static'), name="static")

templates = Jinja2Templates(directory='web_app/templates')


@web_app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
        "is_city": True,
        "is_route_made_by_air": False,
        "time": duration,
        "car_type_id": taxi_class
    })

    price_data = response.get('response_data').get('data')
    return price_data.get('cost')
