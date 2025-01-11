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

def test_insert_item(temp_db):
    item = {"uuid": "1234", "name": "TestItem"}
    result = temp_db.insert_item(item)
    assert result == item

def test_get_item(temp_db):
    item = {"uuid": "5678", "name": "SampleItem"}
    temp_db.insert_item(item)
    fetched_item = temp_db.get_item("5678")
    assert fetched_item["uuid"] == "5678"
    assert fetched_item["name"] == "SampleItem"

def test_update_item(temp_db):
    item = {"uuid": "9999", "name": "OldItem"}
    temp_db.insert_item(item)
    updated_item = temp_db.update_item("9999", {"name": "NewItem"})
    assert updated_item["uuid"] == "9999"
    assert updated_item["name"] == "NewItem"

def test_delete_item(temp_db):
    item = {"uuid": "7777", "name": "ToBeDeleted"}
    temp_db.insert_item(item)
    temp_db.delete_item("7777")
    assert temp_db.get_item("7777") == {}
