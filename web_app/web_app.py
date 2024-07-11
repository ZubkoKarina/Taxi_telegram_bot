from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

web_app = FastAPI()

static_dir = os.path.join(os.path.dirname(__file__), "static")

if not os.path.isdir(static_dir):
    raise RuntimeError(f"Directory '{static_dir}' does not exist")

web_app.mount("/static", StaticFiles(directory='web_app/static'), name="static")

templates = Jinja2Templates(directory='web_app/templates')


@web_app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@web_app.get('/get-api-key')
def get_api_key():
    return {'url': 'https://www.taxiuniversal.com.ua/api'}
