import logging
from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from database.interface import NoSqlDb
from database import TinyDBDatabase
from queues.factory import get_queue_client
from {app_name}.models.{model_name} import {ModelName}, {ModelName}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the database
db: NoSqlDb = TinyDBDatabase()

# Create an item
@router.post("/{model-name}", response_model={ModelName})
def create_{model_name}(item: {ModelName}):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("{model_name}", item_id, new_item)
    logger.info(f"{ModelName} created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/{model-name}s", response_model=List[{ModelName}])
def get_all_{model_name}s():
    logger.info("Received request to retrieve all {model_name}")
    return db.get_all_items("{model_name}")

# Retrieve a single item
@router.get("/{model-name}/{id}", response_model={ModelName})
def get_{model_name}(id: str):
    logger.info(f"Received request to retrieve {model_name} with id: {id}")
    item = db.get_item("{model_name}", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved {model_name}: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/{model-name}/{id}", response_model={ModelName})
def update_{model_name}(id: str, updated_item: {ModelName}):
    item = db.get_item("{model_name}", id)
    logger.info(f"Received request to update {model_name} with id {id}: {updated_item}")
    if not item:
        logger.warning(f"{ModelName} with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("{model_name}", id, updated_item.dict())
    return db.get_item("{model_name}", id)

# Delete an item
@router.delete("/{model-name}/{id}")
def delete_{model_name}(id: str):
    item = db.get_item("{model_name}", id)
    if not item:
        logger.warning(f"{ModelName} with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("{model_name}", id)
    return {"message": "Deleted successfully"}
