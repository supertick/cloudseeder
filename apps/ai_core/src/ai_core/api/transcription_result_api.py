import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from ai_core.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from database import TinyDBDatabase
from queues.factory import get_queue_client
from ai_core.models.transcription_result import Transcription_result, Transcription_result
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Inject database dependency dynamically
def get_db() -> NoSqlDb:
    database_type = settings.database_type  # Read from app config

    db_params: Dict[str, str] = {}

    if database_type == "dynamodb":
        db_params = {
            "region_name": settings.aws_region,
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_access_key
        }
    elif database_type == "tinydb":
        db_params = {
           # "table_prefix": settings.table_prefix
        }


    return get_database(database_type, **db_params)  # Pass to factory


# Create an item
@router.post("/transcription-result", response_model=Transcription_result)
def create_transcription_result(item: Transcription_result, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("transcription_result", item_id, new_item)
    logger.info(f"Transcription_result created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/transcription-results", response_model=List[Transcription_result])
def get_all_transcription_results(db: NoSqlDb = Depends(get_db)):
    logger.info("Received request to retrieve all transcription_result")
    return db.get_all_items("transcription_result")

# Retrieve a single item
@router.get("/transcription-result/{id}", response_model=Transcription_result)
def get_transcription_result(id: str, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to retrieve transcription_result with id: {id}")
    item = db.get_item("transcription_result", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved transcription_result: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/transcription-result/{id}", response_model=Transcription_result)
def update_transcription_result(id: str, updated_item: Transcription_result, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("transcription_result", id)
    logger.info(f"Received request to update transcription_result with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Transcription_result with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("transcription_result", id, updated_item.dict())
    return db.get_item("transcription_result", id)

# Delete an item
@router.delete("/transcription-result/{id}")
def delete_transcription_result(id: str, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("transcription_result", id)
    if not item:
        logger.warning(f"Transcription_result with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("transcription_result", id)
    return {"message": "Deleted successfully"}
