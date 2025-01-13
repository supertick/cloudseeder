import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from ai_core.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from database import TinyDBDatabase
from queues.factory import get_queue_client
from ai_core.models.role import Role, Role

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
@router.post("/role", response_model=Role)
def create_role(item: Role, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("role", item_id, new_item)
    logger.info(f"Role created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/roles", response_model=List[Role])
def get_all_roles():
    logger.info("Received request to retrieve all role")
    return db.get_all_items("role")

# Retrieve a single item
@router.get("/role/{id}", response_model=Role)
def get_role(id: str):
    logger.info(f"Received request to retrieve role with id: {id}")
    item = db.get_item("role", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved role: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/role/{id}", response_model=Role)
def update_role(id: str, updated_item: Role):
    item = db.get_item("role", id)
    logger.info(f"Received request to update role with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Role with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("role", id, updated_item.dict())
    return db.get_item("role", id)

# Delete an item
@router.delete("/role/{id}")
def delete_role(id: str):
    item = db.get_item("role", id)
    if not item:
        logger.warning(f"Role with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("role", id)
    return {"message": "Deleted successfully"}
