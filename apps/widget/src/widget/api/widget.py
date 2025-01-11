from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from packages.database import NoSqlDb
from packages.database import TinyDBDatabase
from packages.queues import QueueFactory


router = APIRouter()

# Initialize the database
db: NoSqlDb = TinyDBDatabase()

class WidgetBase(BaseModel):
    name: str
    description: str

class WidgetResponse(WidgetBase):
    id: str  # Include ID in the response

# Create an item
@router.post("/widget", response_model=WidgetResponse)
def create_widget(item: WidgetBase):
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item(new_item)
    return new_item

# Retrieve all items
@router.get("/widgets", response_model=List[WidgetResponse])
def get_all_widgets():
    return db.get_all_items()

# Retrieve a single item
@router.get("/widget/{id}", response_model=WidgetResponse)
def get_widget(id: str):
    item = db.get_item(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Update an item (without modifying ID)
@router.put("/widget/{id}", response_model=WidgetResponse)
def update_widget(id: str, updated_item: WidgetBase):
    item = db.get_item(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item(id, updated_item.dict())  # Update only name & description
    return db.get_item(id)

# Delete an item
@router.delete("/widget/{id}")
def delete_widget(id: str):
    item = db.get_item(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item(id)
    return {"message": "Deleted successfully"}
