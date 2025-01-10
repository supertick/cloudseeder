import pytest
from fastapi.testclient import TestClient
from {app_name}.main import app

client = TestClient(app)

def test_get_all():
    response = client.get("/v1/{app_name}s")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_item():
    payload = {"name": "Test {AppName}", "description": "A test item"}
    response = client.post("/v1/{app_name}", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Test {AppName}"
    assert response.json()["description"] == "A test item"

def test_get_item_not_found():
    response = client.get("/v1/{app_name}/999")
    assert response.status_code == 404

def test_update_item():
    create_response = client.post("/v1/{app_name}", json={"name": "Old Name", "description": "Old Description"})
    assert create_response.status_code == 200
    item_id = 1  # Assuming first item is assigned ID 1

    update_payload = {"name": "Updated Name", "description": "Updated Description"}
    update_response = client.put(f"/v1/{app_name}/{item_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Name"
    assert update_response.json()["description"] == "Updated Description"

def test_delete_item():
    create_response = client.post("/v1/{app_name}", json={"name": "To Be Deleted", "description": "Will be removed"})
    assert create_response.status_code == 200
    item_id = 1  # Assuming first item is assigned ID 1

    delete_response = client.delete(f"/v1/{app_name}/{item_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Deleted successfully"

    get_response = client.get(f"/v1/{app_name}/{item_id}")
    assert get_response.status_code == 404
