#!/usr/bin/env python3

import os, logging, asyncio

from typing import Optional
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
state.items.get_item('ö', 'russin').uncheck()


with open('token', 'r') as tp:
    security_token = tp.read().strip()


logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'handla-{security_token}.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s')


async def check_token(token: str):
    await asyncio.sleep(1)
    if token != security_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return token


@app.get('/favicon.ico', include_in_schema=False)
async def favicon(request: Request):
    return FileResponse('handlapy/static/favicon.ico')


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
    item = state.items.get_item(category_short, item_name)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if operation == 'check':
        item.check()
    elif operation == 'uncheck':
        item.uncheck()
    print(item)
    return item


@app.get('/s/{token}/edit-itm/{category_short}/{item_name}')
async def edit_item(request: Request, category_short: str, item_name: str, token: str = Depends(check_token)):
    item = state.items.get_item(category_short, item_name)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse('edit_item.html', {
        'request': request,
        'token': token,
        'item': item,
        'categories': state.categories,
    })


@app.get('/{token}', response_class=HTMLResponse)
async def index_legacy(token: str = Depends(check_token)):
    return RedirectResponse(f'/s/{token}/index.html')


@app.get('/s/{token}', response_class=HTMLResponse)
async def index_without_index_html(token: str = Depends(check_token)):
    return RedirectResponse(f'/s/{token}/index.html')


@app.get('/s/{token}/index.html', response_class=HTMLResponse)
async def index_html(request: Request,
                     old_category: Optional[str] = Query(None),
                     new_category: Optional[str] = Query(None),
                     old_name: Optional[str] = Query(None),
                     new_name: Optional[str] = Query(None),
                     new_comment: Optional[str] = Query(None),
                     token: str = Depends(check_token)):

    if old_name != '' and old_category != '':
        print(old_category, old_name)
        item = state.items.get_item(old_category, old_name)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        new_name = new_name.strip()
        new_comment = new_comment.strip()
        item.name = new_name
        item.category = categories[new_category]
        item.comment = new_comment or None

    return templates.TemplateResponse('index.html', {
        'request': request,
        'token': token
    })
