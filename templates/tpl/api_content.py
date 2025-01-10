from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import uuid

router = APIRouter()

# In-memory "database"
fake_db: Dict[str, dict] = {}

class {AppName}(BaseModel):
    id: str  # Include id in response
    name: str
    description: str

# Create an item
@router.post("/{app_name}", response_model={AppName})
def create_{app_name}(item: {AppName}):
    item_id = str(uuid.uuid4())  # Generate a new UUID
    fake_db[item_id] = item.dict()
    fake_db[item_id]["id"] = item_id  # Add ID to stored data
    return fake_db[item_id]

# Retrieve all items
@router.get("/{app_name}s", response_model=List[{AppName}])
def get_all_{app_name}s():
    return list(fake_db.values())

# Retrieve a single item
@router.get("/{app_name}/{{id}}", response_model={AppName})
def get_{app_name}(id: str):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[id]

# Update an item
@router.put("/{app_name}/{{id}}", response_model={AppName})
def update_{app_name}(id: str, updated_item: {AppName}):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    fake_db[id] = updated_item.dict()
    fake_db[id]["id"] = id  # Keep the same ID
    return fake_db[id]

# Delete an item
@router.delete("/{app_name}/{{id}}")
def delete_{app_name}(id: str):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del fake_db[id]
    return {{"message": "Deleted successfully"}}
