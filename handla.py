#!/usr/bin/env python3

import os, asyncio

from typing import Optional
from fastapi import FastAPI, Request, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from handlapy.state import State
from handlapy.category import Categories
from handlapy.item import ItemList, Item, ItemState
from handlapy.db import Database
from handlapy.websocket import ConnectionManager
from handlapy import logging


app = FastAPI()
app.mount('/static/', StaticFiles(directory='handlapy/static'), name='static')
templates = Jinja2Templates(directory='handlapy/templates')


db = Database('handla.db')
categories = Categories.load_from_file('handlapy/data/categories')
state = State(categories, ItemList.with_db(db, categories))
webman = ConnectionManager()


with open('token', 'r') as tp:
    security_token = tp.read().strip()


logger = logging.getLogger(__name__)


async def check_token(token: str):
    #await asyncio.sleep(1)
    if token != security_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return token


@app.get('/favicon.ico', include_in_schema=False)
async def favicon(request: Request):
    logger.info('Favicon')
    return FileResponse('handlapy/static/favicon.ico')


@app.get('/')
def root():
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Det finns inget att se här.")


@app.get('/s/{token}/bootstrap')
def bootstrap(token: str = Depends(check_token)):
    state.items.load_from_file('handlapy/data/things', state.categories)
    return state.items.by_category()


@app.get('/s/{token}/cat')
def read_categories(token: str = Depends(check_token)):
    return state.categories


@app.get('/s/{token}/itm-by-cat')
async def read_items(token: str = Depends(check_token)):
    return await state.items.by_category()


@app.put('/s/{token}/itm/{category_short}/{item_name}/{operation}')
async def mod_item(category_short: str,
                     item_name: str,
                     operation: str,
                     comment: Optional[str] = Query(None),
                     token: str = Depends(check_token)):
    if operation not in ('check', 'uncheck', 'archive', 'add'):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f'Vet inte hur man gör detta: {operation}')
    if operation == 'add':
        category = state.categories[category_short]
        if category is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f'adet finns ingen sån här kategori: {category_short}')
        item = Item(item_name, category, ItemState.unchecked)
        await state.items.add_item(item)
        return item.dict()

    item = await state.items.get_item(category_short, item_name)
    prev = item
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'{category_short}/{item_name} finns inte')
    if operation == 'check':
        item.check()
    elif operation == 'uncheck':
        item.uncheck()
    elif operation == 'archive':
        item.archive()
    if comment is not None:
        item.set_comment(comment)
    await webman.send(dict(old=prev.dict(), new=item.dict()))
    return item.dict()


@app.put('/s/{token}/archive-checked')
async def archive_checked(request: Request, token: str = Depends(check_token)):
    for prev, item in state.items.archive_checked():
        await webman.send(dict(old=prev.dict(), new=item.dict()))


@app.get('/s/{token}/edit-itm/{category_short}/{item_name}')
async def edit_item(request: Request, category_short: str, item_name: str, token: str = Depends(check_token)):
    item = await state.items.get_item(category_short, item_name)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'{category_short}/{item_name} finns inte')
    return templates.TemplateResponse('edit_item.html', {
        'request': request,
        'new': False,
        'token': token,
        'item': item.dict(),
        'categories': state.categories,
    })


@app.get('/s/{token}/new-itm/first/{item_name}')
async def new_item(request: Request, item_name: str, token: str = Depends(check_token)):
    category = state.categories.first()
    item = Item(item_name, category, ItemState.unchecked)
    return templates.TemplateResponse('edit_item.html', {
        'request': request,
        'new': True,
        'token': token,
        'item': item.dict(),
        'categories': state.categories,
    })


@app.get('/s/{token}/delete-itm/{category_short}/{item_name}')
async def delete_item(request: Request, category_short: str, item_name: str, token: str = Depends(check_token)):
    item = await state.items.get_item(category_short, item_name)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'{category_short}/{item_name} finns inte')
    await state.items.delete_item(item)
    await webman.send(dict(old=item.dict(), new=None))
    return RedirectResponse(f'/s/{token}/index.html')


@app.get('/{token}', response_class=HTMLResponse)
async def index_legacy(token: str = Depends(check_token)):
    return RedirectResponse(f'/s/{token}/index.html')


@app.get('/s/{token}', response_class=HTMLResponse)
async def index_without_index_html(token: str = Depends(check_token)):
    return RedirectResponse(f'/s/{token}/index.html')


@app.get('/s/{token}/index.html', response_class=HTMLResponse)
async def index_html(request: Request,
                     is_new: Optional[str] = Query(None),
                     old_category: Optional[str] = Query(None),
                     new_category: Optional[str] = Query(None),
                     old_name: Optional[str] = Query(None),
                     new_name: Optional[str] = Query(None),
                     new_comment: Optional[str] = Query(None),
                     token: str = Depends(check_token)):

    logger.info('index')
    if old_name and old_category:
        print(is_new, old_category, old_name)
        prev = None
        if is_new == 'yes':
            category = state.categories[new_category]
            if category is None:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f'Det finns ingen sån här kategori: {category_short}')
            item = Item(new_name, category, ItemState.unchecked)
            try:
                await state.items.add_item(item)
            except KeyError as e:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
        else:
            item = await state.items.get_item(old_category, old_name)
            prev = item.copy()
            if item is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'{category_short}/{item_name} finns inte')
        new_name = new_name.strip()
        new_comment = new_comment.strip()
        item.rename(new_name)
        item.move(categories[new_category])
        item.set_comment(new_comment)
        await webman.send(dict(old=prev.dict() if prev else None, new=item.dict()))
        return RedirectResponse(f'/s/{token}/index.html')

    return templates.TemplateResponse('index.html', {
        'request': request,
        'token': token
    })


@app.exception_handler(HTTPException)
def error_page(request: Request, exc: HTTPException):
    return templates.TemplateResponse('error.html', {
        'request': request,
        'exc': exc,
    }, status_code=exc.status_code)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await webman.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f'Message text was: {data}')
    except WebSocketDisconnect:
        await webman.disconnect(websocket)


@app.on_event('shutdown')
def on_shutdown():
    #db.close()
    pass
