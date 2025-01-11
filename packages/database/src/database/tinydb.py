from tinydb import TinyDB, Query
from .interface import NoSqlDb

class TinyDBDatabase(NoSqlDb):
    def __init__(self, file_path: str = "db.json"):
        self.db = TinyDB(file_path)

    def insert_item(self, table: str, item: dict) -> dict:
        self.db.table(table).insert(item)
        return item

    def get_item(self, table: str, key: str) -> dict:
        query = Query()
        result = self.db.table(table).search(query.uuid == key)  # Match the uuid field
        return result[0] if result else {}

    def update_item(self, table: str, key: str, updates: dict) -> dict:
        query = Query()
        self.db.table(table).update(updates, query.uuid == key)
        return self.get_item(table, key)

    def delete_item(self, table: str, key: str) -> None:
        query = Query()
        self.db.table(table).remove(query.uuid == key)
