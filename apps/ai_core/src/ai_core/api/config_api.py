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
from ai_core.models.config import Config, Config
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
@router.post("/config", response_model=Config)
def create_config(item: Config, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("config", item_id, new_item)
    logger.info(f"Config created: {new_item}")
    return new_item

# Retrieve all items
@router.get("/configs", response_model=List[Config])
def get_all_configs(db: NoSqlDb = Depends(get_db)):
# def get_all_configs(user: dict = Depends(get_current_user), db: NoSqlDb = Depends(get_db)):
    logger.info("Received request to retrieve all config")
    return db.get_all_items("config")

# Retrieve a single item
@router.get("/config/{id}", response_model=Config)
def get_config(id: str, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to retrieve config with id: {id}")
    item = db.get_item("config", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved config: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/config/{id}", response_model=Config)
def update_config(id: str, updated_item: Config, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("config", id)
    logger.info(f"Received request to update config with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Config with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("config", id, updated_item.dict())
    return db.get_item("config", id)

# Delete an item
@router.delete("/config/{id}")
def delete_config(id: str, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("config", id)
    if not item:
        logger.warning(f"Config with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("config", id)
    return {"message": "Deleted successfully"}
