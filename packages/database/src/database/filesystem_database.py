import os
import json
import logging
import re
from typing import Dict, List, Any, Union

from .interface import NoSqlDb

logger = logging.getLogger(__name__)


class FilesystemDatabase(NoSqlDb):
    def __init__(self, config: Dict[str, str]):
        """
        Initialize the FilesystemDatabase implementation.
        
        Expected configuration keys:
          - base_dir: The base directory path where files will be stored.
                    If not provided, defaults to "data/filesystem_db".
        """
        self.config = config
        self.base_dir = config.get("base_dir", os.path.join("data", "filesystem_db"))
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"FilesystemDatabase initialized with base directory: {self.base_dir}")

    def _get_table_dir(self, table: str) -> str:
        """
        Get the directory path for a given table. Create the directory if it doesn't exist.
        """
        table_dir = os.path.join(self.base_dir, table)
        if not os.path.exists(table_dir):
            os.makedirs(table_dir, exist_ok=True)
        return table_dir

    def _get_file_path(self, table: str, key: str) -> str:
        """
        Construct the file path for a given table and key.
        """
        table_dir = self._get_table_dir(table)
        return os.path.join(table_dir, f"{key}.json")

    def insert_item(self, table: str, key: str, item: dict) -> dict:
        """
        Insert an item into the specified table by writing it as a JSON file.
        The item is stored at: <base_dir>/<table>/<key>.json.
        """
        logger.info(f"Inserting item into table '{table}' with key '{key}': {item}")
        item["id"] = key  # Ensure the key is included in the item.
        file_path = self._get_file_path(table, key)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(item, f)
            logger.info(f"Item inserted successfully at {file_path}")
        except Exception as e:
            logger.exception("Failed to insert item into filesystem")
            raise e
        return item

    def get_item(self, table: str, key: str) -> dict:
        """
        Retrieve an item by key from the specified table.
        
        Returns:
        - A dict if the file is recognized as JSON.
        - Raw bytes if the file is binary or not recognized as JSON.
        - An empty dict if the file does not exist.
        """
        logger.info(f"Retrieving item from table '{table}' with key: {key}")
        file_path = self._get_file_path(table, key)
        
        if not os.path.exists(file_path):
            logger.warning(f"Item with key '{key}' not found in table '{table}'.")
            return {}

        try:
            # Check the file extension to decide if it is JSON.
            if file_path.lower().endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    item = json.load(f)
                logger.info(f"JSON item retrieved: {item}")
                return item
            else:
                with open(file_path, "rb") as f:
                    data = f.read()
                logger.info("Binary or non-JSON data retrieved.")
                return data

        except Exception as e:
            logger.exception("Error reading item from filesystem")
            raise e
        
    def get_binary_item(self, table: str, key: str) -> dict:
        """
        Retrieve an item by key from the specified table.
        
        Returns:
        - A dict if the file is recognized as JSON.
        - Raw bytes if the file is binary or not recognized as JSON.
        - An empty dict if the file does not exist.
        """
        logger.info(f"Retrieving binary item from table '{table}' with key: {key}")
        file_path = self._get_file_path(table, key)
        
        if not os.path.exists(file_path):
            logger.warning(f"Item with key '{key}' not found in table '{table}'.")
            return {}

        try:
            with open(file_path, "rb") as f:
                data = f.read()
            logger.info("Binary or non-JSON data retrieved.")
            return data

        except Exception as e:
            logger.exception("Error reading item from filesystem")
            raise e        

    def get_all_items(self, table: str) -> list:
        """
        Retrieve all items from the specified table.
        Scans the table directory for all JSON files and returns their contents.
        """
        logger.info(f"Retrieving all items from table '{table}'")
        table_dir = self._get_table_dir(table)
        items = []
        try:
            for filename in os.listdir(table_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(table_dir, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        item = json.load(f)
                        items.append(item)
            logger.info(f"Total items retrieved from '{table}': {len(items)}")
            return items
        except Exception as e:
            logger.exception("Error retrieving all items from filesystem")
            raise e

    def update_item(self, table: str, key: str, updates: dict) -> dict:
        """
        Update an item in the specified table by merging the provided updates.
        Returns the updated item.
        """
        logger.info(f"Updating item in table '{table}' with key '{key}' using updates: {updates}")
        item = self.get_item(table, key)
        if not item:
            logger.warning(f"Item with key '{key}' not found in table '{table}', update skipped.")
            return {}
        item.update(updates)
        file_path = self._get_file_path(table, key)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(item, f)
            logger.info(f"Item updated successfully: {item}")
        except Exception as e:
            logger.exception("Failed to update item in filesystem")
            raise e
        return item

    def delete_item(self, table: str, key: str) -> None:
        """
        Delete an item from the specified table by removing its JSON file.
        """
        logger.info(f"Deleting item from table '{table}' with key: {key}")
        file_path = self._get_file_path(table, key)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Item with key '{key}' deleted from table '{table}'")
            else:
                logger.warning(f"Item with key '{key}' not found in table '{table}', nothing to delete.")
        except Exception as e:
            logger.exception("Failed to delete item from filesystem")
            raise e

    def search_by_key_part(self, table: str, key_part: str, regex: bool = False) -> List[Dict[str, Any]]:
        """
        Search for items in the specified table whose keys contain or match a part of the given key.
        If regex is True, treats key_part as a regular expression; otherwise, does a prefix search.
        """
        logger.info(f"Searching in table '{table}' for keys matching: {key_part} (regex={regex})")
        items = self.get_all_items(table)
        if regex:
            pattern = re.compile(key_part)
            matching_items = [item for item in items if "id" in item and pattern.search(item["id"])]
        else:
            matching_items = [item for item in items if "id" in item and item["id"].startswith(key_part)]
        logger.info(f"Found {len(matching_items)} matching items in table '{table}'")
        return matching_items
