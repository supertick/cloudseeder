import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from ai_core.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from database import TinyDBDatabase
from queues.factory import get_queue_client
from ai_core.models.transcription import Transcription, Transcription

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Inject database dependency dynamically
def get_db() -> NoSqlDb:
    database_type = settings.database_type  # Read from app config
    return get_database(database_type)  # Pass to factory


# Create an item
@router.post("/transcription", response_model=Transcription)
def create_transcription(item: Transcription, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("transcription", item_id, new_item)
    logger.info(f"Transcription created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/transcriptions", response_model=List[Transcription])
def get_all_transcriptions(db: NoSqlDb = Depends(get_db)):
    logger.info("Received request to retrieve all transcription")
    return db.get_all_items("transcription")

# Retrieve a single item
@router.get("/transcription/{id}", response_model=Transcription)
def get_transcription(id: str, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to retrieve transcription with id: {id}")
    item = db.get_item("transcription", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved transcription: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/transcription/{id}", response_model=Transcription)
def update_transcription(id: str, updated_item: Transcription, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("transcription", id)
    logger.info(f"Received request to update transcription with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Transcription with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("transcription", id, updated_item.dict())
    return db.get_item("transcription", id)

# Delete an item
@router.delete("/transcription/{id}")
def delete_transcription(id: str, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("transcription", id)
    if not item:
        logger.warning(f"Transcription with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("transcription", id)
    return {"message": "Deleted successfully"}
