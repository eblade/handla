from enum import Enum
from .category import Category, Categories
from itertools import groupby


class ItemState(Enum):
    unchecked = 0
    checked = 1


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
            state=self.state,
            comment=self.comment,
        )

    def __repr__(self):
        x = 'x' if self.state is ItemState.checked else ' '
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
        self._callback(old_name=old_name)

    def move(self, category):
        old_category = self.category.short
        self.category = category
        self._callback(old_category=old_category)

    def check(self):
        self.state = ItemState.checked
        self._callback()

    def uncheck(self):
        self.state = ItemState.unchecked
        self._callback()

    def set_comment(self, comment):
        if not comment:
            self.uncomment()
        else:
            self.comment = comment
        self._callback()
    
    def uncomment(self):
        self.comment = None
        self._callback()

    def is_checked(self):
        return self.state is ItemState.checked

    def is_unchecked(self):
        return self.state is ItemState.unchecked


class ItemList:
    def __init__(self, items: list[Item] = None, db = None):
        self.items = items or []
        self.db = db

    @classmethod
    def load_from_file(cls, path, categories: Categories):
        self = cls()
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
                self.items.append(item)
                item.connect(self)
                keys.add((category_short, name))
        return self

    @classmethod
    def with_db(cls, db, categories: Categories):
        return cls(None, db)

    def by_category(self):
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

    def get_item(self, category_short, item_name):
        return next((item for item in self.items if item.category.short == category_short and item.name == item_name), None)

    def add_item(self, item: Item):
        for existing_item in self.items:
            if item == existing_item:
                raise KeyError(f'Item {item} already exists')
        item.connect(self)
        self.items.append(item)
        self.callback(item.name, item.category.short, item)

    def callback(self, old_name: str, old_category: str, item: Item):
        print('Callback', item)
        if self.db is None:
            return
        self.db.upsert(old_name, old_category, item.name, item.category.short, item.state.value, item.comment)
