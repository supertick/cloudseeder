import logging
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from tinydb.table import Document, Table as TinyDBTable
from uuid import UUID, uuid4
from .interface import NoSqlDb
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomTable(TinyDBTable):
    document_id_class = UUID

    def _get_next_id(self):
        return uuid4()

class CustomDB(TinyDB):
    table_class = CustomTable

class TinyDBDatabase(NoSqlDb):
    def __init__(self, base_dir: str = "databases"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"TinyDB base directory set to: {self.base_dir}")

    def _get_db(self, table: str) -> CustomDB:
        file_path = os.path.join(self.base_dir, f"{table}.json")
        # return CustomDB(file_path, storage=CachingMiddleware(JSONStorage))
        return CustomDB(file_path)

    def insert_item(self, table: str, key: str, item: dict) -> dict:
        logger.info(f"Inserting item into {table} with key {key}: {item}")
        db = self._get_db(table)
        item["id"] = key
        db.insert(Document(item, doc_id=UUID(key)))
        logger.info(f"Item inserted successfully: {item}")
        return item

    def get_item(self, table: str, key: str) -> dict:
        logger.info(f"Retrieving item from {table} with id: {key}")
        db = self._get_db(table)
        result = db.get(doc_id=UUID(key))
        if result:
            logger.info(f"Item retrieved: {result}")
        else:
            logger.warning(f"Item with id {key} not found in {table}")
        return result if result else {}

    def get_all_items(self, table: str) -> list:
        logger.info(f"Retrieving all items from {table}")
        db = self._get_db(table)
        items = db.all()
        logger.info(f"Total items retrieved from {table}: {len(items)}")
        return items

    def update_item(self, table: str, key: str, updates: dict) -> dict:
        logger.info(f"Updating item in {table} with id {key}: {updates}")
        db = self._get_db(table)
        existing_item = self.get_item(table, key)
        if existing_item:
            existing_item.update(updates)
            db.update(existing_item, doc_ids=[UUID(key)])
            logger.info(f"Item updated successfully: {existing_item}")
        else:
            logger.warning(f"Item with id {key} not found in {table}, update skipped")
        return self.get_item(table, key)

    def delete_item(self, table: str, key: str) -> None:
        logger.info(f"Deleting item from {table} with id {key}")
        db = self._get_db(table)
        db.remove(doc_ids=[UUID(key)])
        logger.info(f"Item with id {key} deleted from {table}")
