from .category import Categories, Category
from .item import ItemList, ItemState, Item


class State:
    def __init__(self, categories: Categories, items: ItemList):
        self.categories = categories
        self.items = items
