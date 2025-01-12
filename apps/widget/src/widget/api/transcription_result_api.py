import logging
from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from database.interface import NoSqlDb
from database import TinyDBDatabase
from queues.factory import get_queue_client
from widget.models.transcription_result import Transcription_result, Transcription_resultResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the database
db: NoSqlDb = TinyDBDatabase()

# Create an item
@router.post("/transcription_result", response_model=Transcription_resultResponse)
def create_transcription_result(item: Transcription_result):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("transcription_result", item_id, new_item)
    logger.info(f"Transcription_result created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/transcription_results", response_model=List[Transcription_resultResponse])
def get_all_transcription_results():
    logger.info("Received request to retrieve all transcription_result")
    return db.get_all_items("transcription_result")

# Retrieve a single item
@router.get("/transcription_result/{id}", response_model=Transcription_resultResponse)
def get_transcription_result(id: str):
    logger.info(f"Received request to retrieve transcription_result with id: {id}")
    item = db.get_item("transcription_result", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved transcription_result: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/transcription_result/{id}", response_model=Transcription_resultResponse)
def update_transcription_result(id: str, updated_item: Transcription_result):
    item = db.get_item("transcription_result", id)
    logger.info(f"Received request to update transcription_result with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Transcription_result with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("transcription_result", id, updated_item.dict())
    return db.get_item("transcription_result", id)

# Delete an item
@router.delete("/transcription_result/{id}")
def delete_transcription_result(id: str):
    item = db.get_item("transcription_result", id)
    if not item:
        logger.warning(f"Transcription_result with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("transcription_result", id)
    return {"message": "Deleted successfully"}
