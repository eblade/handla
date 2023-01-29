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

    def __repr__(self):
        x = 'x' if self.state is ItemState.checked else ' '
        comment = f' ({self.comment})' if self.comment else ''
        return f'[{x}] {self.category.short}/{self.name}{comment}'

    def rename(self, name):
        self.name = name

    def move(self, category):
        self.category = category

    def check(self):
        self.state = ItemState.checked

    def uncheck(self):
        self.state = ItemState.unchecked

    def comment(self, comment):
        self.comment = comment
    
    def uncomment(self):
        self.comment = None

    def is_checked(self):
        return self.state is ItemState.checked

    def is_unchecked(self):
        return self.state is ItemState.unchecked


class ItemList:
    def __init__(self, items: list[Item] = None):
        self.items = items or []

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
                keys.add((category_short, name))
        return self

    def by_category(self):
        in_order = sorted((item for item in self.items), key=lambda x: (x.category.ordinal, x.name))
        grouped = groupby(in_order, lambda x: x.category)
        return {
            'categories': [
                {
                    'name': group[0].name,
                    'short': group[0].short,
                    'items': [item for item in group[1]]
                } for group in grouped
            ]
        }

    def get_item(self, category_short, item_name):
        return next((item for item in self.items if item.category.short == category_short and item.name == item_name), None)
