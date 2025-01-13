import logging
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from ai_core.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from database import TinyDBDatabase
from queues.factory import get_queue_client
from ai_core.models.transcription_result import Transcription_result, Transcription_result
from typing import Dict
from auth.factory import get_auth_provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

auth = get_auth_provider()
security = HTTPBearer()

# Authentication dependency - FIXME probably not good to have this replicated in every model
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Get current authenticated user from token."""
    token = credentials.credentials
    user = auth.get_user(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user

# Role-based access control (RBAC) dependency
def require_role(required_roles: List[str]):
    """Dependency factory for role-based access control."""
    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in required_roles:
            raise HTTPException(status_code=403, detail="Access denied: Insufficient permissions")
        return user
    return role_checker


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
# def get_all_transcription_results(user: dict = Depends(get_current_user), db: NoSqlDb = Depends(get_db)):
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
