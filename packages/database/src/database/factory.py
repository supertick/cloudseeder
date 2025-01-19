from typing import Dict
from .interface import NoSqlDb
# from app.config import settings  # Ensure settings are accessible here
from typing import Callable, Dict
from database.interface import NoSqlDb
from database.tinydb import TinyDBDatabase
from database.dynamodb_database import DynamoDBDatabase  # Import DynamoDB implementation


def get_database(config_provider: Callable[[], Dict[str, str]]) -> NoSqlDb:
    """Factory method to return a NoSqlDb implementation based on the type."""
    config = config_provider()  # Get configuration dynamically
    database_type = config.get("database_type", "").lower()
    if database_type == "dynamodb":
        return DynamoDBDatabase(config=config)
    elif database_type == "tinydb":
        return TinyDBDatabase(config=config)
    else:
        raise ValueError(f"Unsupported database type: {database_type}")

def get_db(config_provider: Callable[[], Dict[str, str]]) -> NoSqlDb:
    """
    Load database implementation dynamically based on a configuration provider.

    :param config_provider: A callable that returns the database configuration.
    :return: An instance of NoSqlDb.
    """
    # config = config_provider()  # Get configuration dynamically
    # database_type = config.get("database_type", "").lower()
    # db_params: Dict[str, str] = {k: v for k, v in config.items() if k != "database_type"}

    return get_database(config_provider=config_provider)