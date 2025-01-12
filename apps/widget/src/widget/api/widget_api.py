import logging
from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from database.interface import NoSqlDb
from database import TinyDBDatabase
from queues.factory import get_queue_client
from widget.models.widget import Widget, WidgetResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the database
db: NoSqlDb = TinyDBDatabase()

# Create an item
@router.post("/widget", response_model=WidgetResponse)
def create_widget(item: Widget):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("widget", item_id, new_item)
    logger.info(f"Widget created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/widgets", response_model=List[WidgetResponse])
def get_all_widgets():
    logger.info("Received request to retrieve all widget")
    return db.get_all_items("widget")

# Retrieve a single item
@router.get("/widget/{id}", response_model=WidgetResponse)
def get_widget(id: str):
    logger.info(f"Received request to retrieve widget with id: {id}")
    item = db.get_item("widget", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved widget: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/widget/{id}", response_model=WidgetResponse)
def update_widget(id: str, updated_item: Widget):
    item = db.get_item("widget", id)
    logger.info(f"Received request to update widget with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Widget with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("widget", id, updated_item.dict())
    return db.get_item("widget", id)

# Delete an item
@router.delete("/widget/{id}")
def delete_widget(id: str):
    item = db.get_item("widget", id)
    if not item:
        logger.warning(f"Widget with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("widget", id)
    return {"message": "Deleted successfully"}
