import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from ai_core.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from database import TinyDBDatabase
from queues.factory import get_queue_client
from ai_core.models.user import User, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Inject database dependency dynamically
def get_db() -> NoSqlDb:
    database_type = settings.database_type  # Read from app config
    return get_database(database_type)  # Pass to factory


# Create an item
@router.post("/user", response_model=User)
def create_user(item: User, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("user", item_id, new_item)
    logger.info(f"User created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/users", response_model=List[User])
def get_all_users(db: NoSqlDb = Depends(get_db)):
    logger.info("Received request to retrieve all user")
    return db.get_all_items("user")

# Retrieve a single item
@router.get("/user/{id}", response_model=User)
def get_user(id: str, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to retrieve user with id: {id}")
    item = db.get_item("user", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved user: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/user/{id}", response_model=User)
def update_user(id: str, updated_item: User, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("user", id)
    logger.info(f"Received request to update user with id {id}: {updated_item}")
    if not item:
        logger.warning(f"User with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("user", id, updated_item.dict())
    return db.get_item("user", id)

# Delete an item
@router.delete("/user/{id}")
def delete_user(id: str, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("user", id)
    if not item:
        logger.warning(f"User with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("user", id)
    return {"message": "Deleted successfully"}
