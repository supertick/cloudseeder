import os
import pytest
from database.tinydb import TinyDBDatabase

@pytest.fixture
def temp_db():
    """Creates a temporary database for testing."""
    db_file = "test_db.json"
    db = TinyDBDatabase(db_file)
    yield db
    os.remove(db_file)  # Cleanup after test
