from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from database.interface import NoSqlDb
from database import TinyDBDatabase
from queues.factory import get_queue_client
from {app_name}.models.{app_name} import {AppName}, WidgetResponse


router = APIRouter()

# Initialize the database
db: NoSqlDb = TinyDBDatabase()

# class {AppName}(BaseModel):
#     name: str
#     description: str

# class {AppName}Response({AppName}):
#     id: str  # Include ID in the response

# Create an item
@router.post("/{app_name}", response_model={AppName}Response)
def create_{app_name}(item: {AppName}):
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("{app_name}", new_item)
    return new_item

# Retrieve all items
@router.get("/{app_name}s", response_model=List[{AppName}Response])
def get_all_{app_name}s():
    return db.get_all_items("{app_name}")

# Retrieve a single item
@router.get("/{app_name}/{id}", response_model={AppName}Response)
def get_{app_name}(id: str):
    item = db.get_item("{app_name}", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Update an item (without modifying ID)
@router.put("/{app_name}/{id}", response_model={AppName}Response)
def update_{app_name}(id: str, updated_item: {AppName}):
    item = db.get_item("{app_name}", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item(id, updated_item.dict())  # Update only name & description
    return db.get_item("{app_name}", id)

# Delete an item
@router.delete("/{app_name}/{id}")
def delete_{app_name}(id: str):
    item = db.get_item("{app_name}", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("{app_name}", id)
    return {"message": "Deleted successfully"}
