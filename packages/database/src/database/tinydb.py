from typing import List, Dict, Any
import logging
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from tinydb.table import Document, Table as TinyDBTable
from .interface import NoSqlDb
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomTable(TinyDBTable):
    document_id_class = str  # Enforce string-based doc_id

class CustomDB(TinyDB):
    table_class = CustomTable  # Use CustomTable with string-based doc_id

class TinyDBDatabase(NoSqlDb):
    def __init__(self, config: Dict[str, str]):
        base_dir: str = os.path.join("data", "databases")
        self.config = config
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
        item["id"] = key  # Ensure the key is included in the item
        inserted_id = db.insert(Document(item, doc_id=key))  # Use key directly as doc_id
        logger.info(f"Item inserted successfully with doc_id={inserted_id}: {item}")
        return item

    def get_item(self, table: str, key: str) -> dict:
        logger.info(f"Retrieving item from {table} with id: {key}")
        db = self._get_db(table)
        result = db.get(doc_id=key)  # Use string-based doc_id
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
            db.update(existing_item, doc_ids=[key])  # Use string-based doc_id
            logger.info(f"Item updated successfully: {existing_item}")
        else:
            logger.warning(f"Item with id {key} not found in {table}, update skipped")
        return self.get_item(table, key)

    def delete_item(self, table: str, key: str) -> None:
        logger.info(f"Deleting item from {table} with id {key}")
        db = self._get_db(table)
        db.remove(doc_ids=[key])  # Use string-based doc_id
        logger.info(f"Item with id {key} deleted from {table}")

    def search_by_key_part(self, table: str, key_part: str, regex: bool = False) -> List[Dict[str, Any]]:
        """
        Search for items whose keys contain or match a part of the given key.

        :param table: The table to search in.
        :param key_part: The key part to search for.
        :param regex: Whether to treat key_part as a regular expression. Defaults to False (prefix search).
        :return: A list of matching items.
        """
        logger.info(f"Searching in {table} for keys matching: {key_part} (regex={regex})")
        db = self._get_db(table)
        items = db.all()

        if regex:
            # Perform a regex search on the "id" field
            pattern = re.compile(key_part)
            matching_items = [item for item in items if "id" in item and pattern.search(item["id"])]
        else:
            # Default to a prefix match
            matching_items = [item for item in items if "id" in item and item["id"].startswith(key_part)]

        logger.info(f"Found {len(matching_items)} matching items in {table}")
        return matching_items