import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from ai_core.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from database import TinyDBDatabase
from queues.factory import get_queue_client
from ai_core.models.company import Company, Company

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the database
db: NoSqlDb = TinyDBDatabase()

# Inject database dependency dynamically
def get_db() -> NoSqlDb:
    database_type = settings.database_type  # Read from app config
    return get_database(database_type)  # Pass to factory


# Create an item
@router.post("/company", response_model=Company)
def create_company(item: Company, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("company", item_id, new_item)
    logger.info(f"Company created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/companys", response_model=List[Company])
def get_all_companys():
    logger.info("Received request to retrieve all company")
    return db.get_all_items("company")

# Retrieve a single item
@router.get("/company/{id}", response_model=Company)
def get_company(id: str):
    logger.info(f"Received request to retrieve company with id: {id}")
    item = db.get_item("company", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved company: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/company/{id}", response_model=Company)
def update_company(id: str, updated_item: Company):
    item = db.get_item("company", id)
    logger.info(f"Received request to update company with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Company with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("company", id, updated_item.dict())
    return db.get_item("company", id)

# Delete an item
@router.delete("/company/{id}")
def delete_company(id: str):
    item = db.get_item("company", id)
    if not item:
        logger.warning(f"Company with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("company", id)
    return {"message": "Deleted successfully"}
