from abc import ABC, abstractmethod

class NoSqlDb(ABC):
    @abstractmethod
    def insert_item(self, table: str, item: dict) -> dict:
        pass

    @abstractmethod
    def get_item(self, table: str, key: str) -> dict:
        pass

    @abstractmethod
    def update_item(self, table: str, key: str, updates: dict) -> dict:
        pass

    @abstractmethod
    def delete_item(self, table: str, key: str) -> None:
        pass
