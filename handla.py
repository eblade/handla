#!/usr/bin/env python3

import os, logging, asyncio

from fastapi import FastAPI, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from handlapy.state import State
from handlapy.category import Categories
from handlapy.item import ItemList


app = FastAPI()
app.mount('/static/', StaticFiles(directory='handlapy/static'), name='static')
templates = Jinja2Templates(directory='handlapy/templates')


categories = Categories.load_from_file('handlapy/data/categories')
state = State(categories, ItemList.load_from_file('handlapy/data/things', categories))


with open('token', 'r') as tp:
    security_token = tp.read().strip()


logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'rthserve-{security_token}.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s')


def check_token(token: str):
    if token != security_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return token


@app.get('/s/{token}/cat')
def read_categories(token: str = Depends(check_token)):
    return state.categories


@app.get('/s/{token}/itm-by-cat')
def read_items(token: str = Depends(check_token)):
    return state.items.by_category()


@app.put('/s/{token}/itm/{category_short}/{item_name}/{operation}')
async def read_items(category_short: str, item_name: str, operation: str, token: str = Depends(check_token)):
    if operation not in ('check', 'uncheck'):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    await asyncio.sleep(1)
    item = state.items.get_item(category_short, item_name)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if operation == 'check':
        item.check()
    elif operation == 'uncheck':
        item.uncheck()
    print(item)
    return item


@app.get('/s/{token}', response_class=HTMLResponse)
async def index_without_index_html(token: str = Depends(check_token)):
    return RedirectResponse(f'/{token}/index.html')


@app.get('/s/{token}/index.html', response_class=HTMLResponse)
async def index_html(request: Request, token: str = Depends(check_token)):
    return templates.TemplateResponse('index.html', {
        'request': request,
        'token': token
    })


@app.get('/favicon.ico', include_in_schema=False)
async def favicon(request: Request):
    return FileResponse('handlapy/static/favicon.ico')
