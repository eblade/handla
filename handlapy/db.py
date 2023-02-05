import sqlite3
import os


class Database:
    def __init__(self, path: str):
        self.path = path
        self._con = sqlite3.connect(path)
        self.setup()

    def close(self):
        print("Closing the connection")
        self._con.commit()
        self._con.close()

    def cursor(self):
        return self._con.cursor()

    def setup(self):
        print("Setup")
        cur = self.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS item(name, category, state INTEGER, comment)")
        cur.close()

    def upsert(self, old_name: str, old_category: str, name: str, category: str, state: int, comment: str):
        print("upsert")
        cur = self.cursor()
        params = (old_name, old_category)
        res = cur.execute("SELECT * FROM item WHERE name = ? AND category = ?", params)
        existing = res.fetchone()
        cur.close()
        if existing is None:
            self.insert(name, category, state, comment)
        else:
            self.update(old_name, old_category, name, category, state, comment)

    def insert(self, name: str, category: str, state: int, comment: str):
        print("insert")
        cur = self.cursor()
        params = dict(name=name, category=category, state=state, comment=comment)
        res = cur.execute("INSERT INTO item VALUES(:name, :category, :state, :comment)", params)
        cur.close()
        self._con.commit()

    def update(self, old_name: str, old_category: str, name: str, category: str, state: int, comment: str):
        cur = self.cursor()
        params = (name, category, state, comment, old_name, old_category)
        res = cur.execute("UPDATE item SET name = ?, category = ?, state = ?, comment = ? WHERE name = ? AND category = ?", params)
        cur.close()
        self._con.commit()

