from tinydb import TinyDB, Query
from .interface import NoSqlDb

class TinyDBDatabase(NoSqlDb):
    def __init__(self, file_path: str = "db.json"):
        self.db = TinyDB(file_path)
        self.table = self.db.table("widgets")

    def insert_item(self, item: dict) -> dict:
        self.table.insert(item)
        return item

    def get_item(self, key: str) -> dict:
        query = Query()
        result = self.table.search(query.uuid == key)  # Match the uuid field
        return result[0] if result else {}

    def update_item(self, key: str, updates: dict) -> dict:
        query = Query()
        self.table.update(updates, query.uuid == key)
        return self.get_item(key)

    def delete_item(self, key: str) -> None:
        query = Query()
        self.table.remove(query.uuid == key)
