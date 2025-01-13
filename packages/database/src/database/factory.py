from database.interface import NoSqlDb
from database.tinydb import TinyDBDatabase
from database.dynamodb_database import DynamoDBDatabase  # Import DynamoDB implementation

def get_database(database_type: str, **kwargs) -> NoSqlDb:
    """Factory function that returns a database instance based on the type."""
    if database_type == "tinydb":
        return TinyDBDatabase()
    elif database_type == "dynamodb":
        return DynamoDBDatabase(**kwargs)
    else:
        raise ValueError(f"Unsupported database type: {database_type}")
