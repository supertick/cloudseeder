from abc import ABC, abstractmethod

class NoSqlDb(ABC):
    @abstractmethod
    def insert_item(self, item: dict) -> dict:
        pass

    @abstractmethod
    def get_item(self, key: str) -> dict:
        pass

    @abstractmethod
    def update_item(self, key: str, updates: dict) -> dict:
        pass

    @abstractmethod
    def delete_item(self, key: str) -> None:
        pass
