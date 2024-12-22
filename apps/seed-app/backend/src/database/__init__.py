import os
from .dynamodb import DynamoDBDatabase
from .tinydb import TinyDBDatabase

def get_database():
    backend = os.getenv("NOSQL_BACKEND", "tinydb").lower()
    if backend == "dynamodb":
        return DynamoDBDatabase(table_name="widgets")
    return TinyDBDatabase()
