import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from ai_core.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from database import TinyDBDatabase
from queues.factory import get_queue_client
from ai_core.models.transcription_request import Transcription_request, Transcription_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Inject database dependency dynamically
def get_db() -> NoSqlDb:
    database_type = settings.database_type  # Read from app config
    return get_database(database_type)  # Pass to factory


# Create an item
@router.post("/transcription-request", response_model=Transcription_request)
def create_transcription_request(item: Transcription_request, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("transcription_request", item_id, new_item)
    logger.info(f"Transcription_request created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/transcription-requests", response_model=List[Transcription_request])
def get_all_transcription_requests(db: NoSqlDb = Depends(get_db)):
    logger.info("Received request to retrieve all transcription_request")
    return db.get_all_items("transcription_request")

# Retrieve a single item
@router.get("/transcription-request/{id}", response_model=Transcription_request)
def get_transcription_request(id: str, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to retrieve transcription_request with id: {id}")
    item = db.get_item("transcription_request", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved transcription_request: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/transcription-request/{id}", response_model=Transcription_request)
def update_transcription_request(id: str, updated_item: Transcription_request, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("transcription_request", id)
    logger.info(f"Received request to update transcription_request with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Transcription_request with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("transcription_request", id, updated_item.dict())
    return db.get_item("transcription_request", id)

# Delete an item
@router.delete("/transcription-request/{id}")
def delete_transcription_request(id: str, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("transcription_request", id)
    if not item:
        logger.warning(f"Transcription_request with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("transcription_request", id)
    return {"message": "Deleted successfully"}
