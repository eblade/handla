import sqlite3
import os
import threading
from contextlib import closing


class Database:
    def __init__(self, path: str):
        self.path = path
        self.lock = threading.Lock()
        self.setup()

    def connect(self):
        return sqlite3.connect(self.path)

    def setup(self):
        with self.lock:
            with closing(self.connect()) as con:
                with closing(con.cursor()) as cur:
                    cur.execute("CREATE TABLE IF NOT EXISTS item(name, category, state INTEGER, comment)")
                con.commit()

    def select(self, factory):
        with self.lock:
            with closing(self.connect()) as con:
                with closing(con.cursor()) as cur:
                     yield from (factory(*row) for row in cur.execute("SELECT * FROM item"))

    def upsert(self, old_name: str, old_category: str, name: str, category: str, state: int, comment: str):
        with self.lock:
            with closing(self.connect()) as con:
                with closing(con.cursor()) as cur:
                    params = (old_name, old_category)
                    res = cur.execute("SELECT * FROM item WHERE name = ? AND category = ?", params)
                    existing = res.fetchone()
                    if existing is None:
                        self.insert(cur, name, category, state, comment)
                    else:
                        self.update(cur, old_name, old_category, name, category, state, comment)
                con.commit()

    def insert(self, cur, name: str, category: str, state: int, comment: str):
        params = dict(name=name, category=category, state=state, comment=comment)
        res = cur.execute("INSERT INTO item VALUES(:name, :category, :state, :comment)", params)

    def update(self, cur, old_name: str, old_category: str, name: str, category: str, state: int, comment: str):
        params = (name, category, state, comment, old_name, old_category)
        res = cur.execute("UPDATE item SET name = ?, category = ?, state = ?, comment = ? WHERE name = ? AND category = ?", params)

    def delete(self, name: str, category: str):
        with self.lock:
            with closing(self.connect()) as con:
                with closing(con.cursor()) as cur:
                    params = (name, category)
                    res = cur.execute("DELETE FROM item WHERE name = ? AND category = ?", params)
                con.commit()

