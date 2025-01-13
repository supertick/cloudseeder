from database.interface import NoSqlDb
from database.tinydb import TinyDBDatabase  # TinyDB implementation
# from database.dynamodb_database import DynamoDBDatabase  # Future example

def get_database(database_type: str) -> NoSqlDb:
    """Factory function that returns a database instance based on the type."""
    if database_type == "tinydb":
        return TinyDBDatabase()
    elif database_type == "dynamodb":
        return DynamoDBDatabase()  # Example for a real cloud DB
    else:
        raise ValueError(f"Unsupported database type: {database_type}")
