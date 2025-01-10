from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import uuid

router = APIRouter()

# In-memory "database"
fake_db: Dict[str, dict] = {}

class {AppName}Base(BaseModel):
    name: str
    description: str

class {AppName}Response({AppName}Base):
    id: str  # Include ID in the response

# Create an item
@router.post("/{app_name}", response_model={AppName}Response)
def create_{app_name}(item: {AppName}Base):
    item_id = str(uuid.uuid4())  # Generate a new UUID
    fake_db[item_id] = item.dict()
    fake_db[item_id]["id"] = item_id  # Store ID in the database
    return fake_db[item_id]

# Retrieve all items
@router.get("/{app_name}s", response_model=List[{AppName}Response])
def get_all_{app_name}s():
    return list(fake_db.values())

# Retrieve a single item
@router.get("/{app_name}/{id}", response_model={AppName}Response)
def get_{app_name}(id: str):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[id]

# Update an item (without modifying ID)
@router.put("/{app_name}/{id}", response_model={AppName}Response)
def update_{app_name}(id: str, updated_item: {AppName}Base):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Only update name & description, keep existing ID
    fake_db[id].update(updated_item.dict())
    return fake_db[id]

# Delete an item
@router.delete("/{app_name}/{id}")
def delete_{app_name}(id: str):
    if id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del fake_db[id]
    return {"message": "Deleted successfully"}
