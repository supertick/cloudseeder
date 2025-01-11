from abc import ABC, abstractmethod

class NoSqlDb(ABC):
    @abstractmethod
    def insert_item(self, table: str, item: dict) -> dict:
        """Insert an item into the specified table."""
        pass

    @abstractmethod
    def get_item(self, table: str, key: str) -> dict:
        """Retrieve an item by its key from the specified table."""
        pass

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
