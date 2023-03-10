import asyncio
from enum import Enum
from . import logging
from .category import Category, Categories
from itertools import groupby
from typing import List


logger = logging.getLogger(__name__)


class ItemState(Enum):
    unchecked = 0
    archived = 1
    checked = 2


class Item:
    def __init__(self, name: str, category: Category, state: ItemState = ItemState.checked, comment: str = None):
        self.name = name
        self.category = category
        self.state = state
        self.comment = comment
        self._parent = None

    def dict(self):
        return dict(
            name=self.name,
            category=self.category.dict(),
            state=self.state.value,
            comment=self.comment,
        )

    def copy(self):
        return Item(self.name, self.category, self.state, self.comment)

    @classmethod
    def from_db(self, categories: Categories, name: str, category_short: str, state_value: int, comment: str):
        category = categories[category_short]
        state = {
            0: ItemState.unchecked,
            1: ItemState.archived,
            2: ItemState.checked,
        }.get(state_value, 0)
        return Item(name, category, state, comment)

    def __repr__(self):
        x = {
            ItemState.checked: 'x',
            ItemState.archived: '-',
            ItemState.unchecked: ' ',
        }.get(self.state)
        comment = f' ({self.comment})' if self.comment else ''
        return f'[{x}] {self.category.short}/{self.name}{comment}'

    def __eq__(self, other):
        return self.category.short == other.category.short and self.name == other.name

    def connect(self, parent):
        self._parent = parent

    def _callback(self, old_name=None, old_category=None):
        if self._parent is not None:
            self._parent.callback(old_name or self.name, old_category or self.category.short, self)

    def rename(self, name):
        old_name = self.name
        self.name = name
        if old_name != name:
            logger.debug(f'{old_name} -> {name}')
            self._callback(old_name=old_name)

    def move(self, category):
        old_category = self.category.short
        self.category = category
        if old_category != category.short:
            logger.debug(f'{self.name} {old_category} -> {category}')
            self._callback(old_category=old_category)

    def check(self):
        if self.state is ItemState.checked:
            return
        self.state = ItemState.checked
        logger.debug(repr(self))
        self._callback()

    def uncheck(self):
        if self.state is ItemState.unchecked:
            return
        self.state = ItemState.unchecked
        logger.debug(repr(self))
        self._callback()

    def archive(self):
        if self.state is ItemState.archived:
            return
        self.state = ItemState.archived
        self.comment = None
        logger.debug(repr(self))
        self._callback()

    def set_comment(self, comment):
        if not comment:
            self.uncomment()
        else:
            if self.comment == comment:
                return
            self.comment = comment
            logger.debug(repr(self))
            self._callback()

    def uncomment(self):
        if self.comment is None:
            return
        self.comment = None
        logger.debug(repr(self))
        self._callback()

    def is_checked(self):
        return self.state is ItemState.checked

    def is_unchecked(self):
        return self.state is ItemState.unchecked


class ItemList:
    def __init__(self, items: List[Item] = None, db = None):
        self.items = list(items) or []
        for item in self.items:
            item.connect(self)
        self.db = db
        self._lock = asyncio.Lock()

    def load_from_file(self, path, categories: Categories):
        keys = set()
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                category_short, name = line.split(maxsplit=1)
                category_short = category_short.strip()
                name = name.strip()
                if category_short not in categories:
                    raise KeyError(f'Category not found: {category_short}')
                if (category_short, name) in keys:
                    raise KeyError(f'Duplicate name: {category_short}/{name}')
                category = categories[category_short]
                item = Item(name, category, ItemState.checked)
                self.add_item(item)
                keys.add((category_short, name))

    @classmethod
    def with_db(cls, db, categories: Categories):
        return cls(db.select(lambda *data: Item.from_db(categories, *data)), db)

    async def by_category(self):
        async with self._lock:
            in_order = sorted((item for item in self.items), key=lambda x: (x.category.ordinal, x.name))
            grouped = groupby(in_order, lambda x: x.category)
            return {
                'categories': [
                    {
                        'name': group[0].name,
                        'short': group[0].short,
                        'items': [item.dict() for item in group[1]]
                    } for group in grouped
                ]
            }

    async def get_item(self, category_short, item_name):
        async with self._lock:
            return next((item for item in self.items if item.category.short == category_short and item.name == item_name), None)

    async def add_item(self, item: Item):
        async with self._lock:
            for existing_item in self.items:
                if item == existing_item:
                    raise KeyError(f'Item {item} already exists')
            item.connect(self)
            self.items.append(item)
            self.callback(item.name, item.category.short, item)

    async def delete_item(self, item: Item):
        async with self._lock:
            self.items.remove(item)
            self.db.delete(item.name, item.category.short)

    async def archive_all_checked(self):
        logger.debug('Archiving checked items')
        async with self._lock:
            for item in self.items:
                if item.state is ItemState.checked:
                    prev = item.copy()
                    item.archive()
                    yield prev, item

    def callback(self, old_name: str, old_category: str, item: Item):
        if self.db is None:
            return
        self.db.upsert(old_name, old_category, item.name, item.category.short, item.state.value, item.comment)
