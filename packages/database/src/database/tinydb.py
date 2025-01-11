from tinydb import TinyDB, Query
from .interface import NoSqlDb

class TinyDBDatabase(NoSqlDb):
    def __init__(self, file_path: str = "db.json"):
        self.db = TinyDB(file_path)

    def insert_item(self, table: str, item: dict) -> dict:
        table_ref = self.db.table(table)
        item_id = item.get("id")
        if not item_id:
            raise ValueError("Item must have an 'id' field")
        table_ref.update({item_id: item}, Query().id == item_id)
        if not self.get_item(table, item_id):
            table_ref.insert(item)
        return item

    def get_item(self, table: str, key: str) -> dict:
        table_ref = self.db.table(table)
        result = next((item for item in table_ref.all() if item.get("id") == key), None)
        return result if result else {}

    def get_all_items(self, table: str) -> list:
        return self.db.table(table).all()

    def update_item(self, table: str, key: str, updates: dict) -> dict:
        table_ref = self.db.table(table)
        existing_item = self.get_item(table, key)
        if existing_item:
            existing_item.update(updates)
            self.insert_item(table, existing_item)
        return self.get_item(table, key)

    def delete_item(self, table: str, key: str) -> None:
        table_ref = self.db.table(table)
        table_ref.remove(Query().id == key)
