import sqlite3
import os
import json
import threading
from . import logging
from contextlib import closing


logger = logging.getLogger(__name__)


class Database:
    def __init__(self, path: str):
        self.path = path
        self.lock = threading.Lock()
        self.setup()

    def connect(self):
        return sqlite3.connect(self.path)

    def setup(self):
        logger.info('Setting up database')
        with self.lock:
            with closing(self.connect()) as con:
                with closing(con.cursor()) as cur:
                    cur.execute("CREATE TABLE IF NOT EXISTS item(name, category, state INTEGER, comment)")
                con.commit()
        logger.info('Done setting up database')

    def select(self, factory):
        with self.lock:
            with closing(self.connect()) as con:
                with closing(con.cursor()) as cur:
                     yield from (factory(*row) for row in cur.execute("SELECT * FROM item"))

    def upsert(self, old_name: str, old_category: str, name: str, category: str, state: int, comment: str):
        logger.debug(fmt(dict(
            old_name=old_name,
            old_category=old_category,
            name=name,
            category=category,
            state=state,
            comment=comment)))
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
        logger.debug(fmt(dict(
            name=name,
            category=category,
            state=state,
            comment=comment)))
        params = dict(name=name, category=category, state=state, comment=comment)
        res = cur.execute("INSERT INTO item VALUES(:name, :category, :state, :comment)", params)

    def update(self, cur, old_name: str, old_category: str, name: str, category: str, state: int, comment: str):
        logger.debug(fmt(dict(
            old_name=old_name,
            old_category=old_category,
            name=name,
            category=category,
            state=state,
            comment=comment)))
        params = (name, category, state, comment, old_name, old_category)
        res = cur.execute("UPDATE item SET name = ?, category = ?, state = ?, comment = ? WHERE name = ? AND category = ?", params)

    def delete(self, name: str, category: str):
        logger.debug(fmt(dict(
            name=name,
            category=category)))
        with self.lock:
            with closing(self.connect()) as con:
                with closing(con.cursor()) as cur:
                    params = (name, category)
                    res = cur.execute("DELETE FROM item WHERE name = ? AND category = ?", params)
                con.commit()


def fmt(dct):
    return json.dumps(dct, indent=2)
