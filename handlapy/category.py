class Category:
    def __init__(self, name: str, short: str, ordinal: int):
        self.name = name
        self.short = short
        self.ordinal = ordinal

    def __repr__(self):
        return f'[{self.short}] {self.name}'


class Categories:
    def __init__(self, categories: list[Category] = None):
        self.categories = categories or []
        self._indexed = False
        self._index = {}

    def _make_index(self):
        self._index = {cat.short: cat for cat in self.categories}
        self._indexed = True

    def __getitem__(self, key):
        if not self._indexed:
            self._make_index()
        return self._index[key]

    def __contains__(self, key):
        if not self._indexed:
            self._make_index()
        return key in self._index

    def __iter__(self):
        return iter(self.categories)

    def first(self):
        return self.categories[0]


    @classmethod
    def load_from_file(cls, path):
        self = cls()
        keys = set()
        with open(path, 'r') as f:
            ordinal = 0
            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue
                elif line.startswith('#'):
                    continue
                short, name = line.split(maxsplit=1)
                short = short.strip()
                name = name.strip()
                if short in keys:
                    raise KeyError(f'Duplicate category key: {short}')
                category = Category(name, short, ordinal)
                ordinal += 1
                keys.add(short)
                self.categories.append(category)
        return self
