from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union

class NoSqlDb(ABC):
    @abstractmethod
    def insert_item(self, table: str, key:str, item: dict) -> dict:
        """Insert an item into the specified table."""
        pass

    @abstractmethod
    def get_item(self, table: str, key: str) -> dict:
        """Retrieve an item by its key from the specified table."""
        pass

    def get_binary_item(self, table: str, key: str) -> bytes:
        """Retrieve an item by its key from the specified table."""

    @abstractmethod
    def get_all_items(self, table: str) -> list:
        """Retrieve all items from the specified table."""
        pass

    @abstractmethod
    def update_item(self, table: str, key: str, updates: dict) -> dict:
        """Update an item in the specified table."""
        pass

    @abstractmethod
    def delete_item(self, table: str, key: str) -> None:
        """Delete an item from the specified table by its key."""
        pass

    @abstractmethod
    def search_by_key_part(
        self, table: str, key_part: str, regex: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for items whose keys contain or match a part of the given key.

        :param table: The table to search in.
        :param key_part: The key part to search for.
        :param regex: Whether to treat key_part as a regular expression. Defaults to False (prefix search).
        :return: A list of matching items.
        """
        pass