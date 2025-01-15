import logging
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from {app_name}.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from queues.factory import get_queue_client
from queues.interface import QueueClient
from {app_name}.models.{model_name} import {ModelName}, {ModelName}
from typing import Dict
from auth.factory import get_auth_provider
from ..auth_util import get_current_user, require_role
    
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

auth = get_auth_provider()
security = HTTPBearer()

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


# Inject database dependency dynamically
def get_queue() -> QueueClient:
    queue_type = settings.queue_type  # Read from app config

    q_params: Dict[str, str] = {}

    if not queue_type:
        return None

    if queue_type == "local":
        q_params = {}
    elif queue_type == "sqs":
        q_params = {
           # aws stuff
        }

    return get_queue_client(name="{ModelName}", queue_type="local", **q_params)  # Pass to factory



# Create an item
@router.post("/{model-name}", response_model={ModelName})
def create_{model_name}(item: {ModelName}, db: NoSqlDb = Depends(get_db), q: QueueClient = Depends(get_queue), user: dict = Depends(require_role(["admin"]))):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("{model_name}", item_id, new_item)
    logger.info(f"{ModelName} created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: {ModelName} created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# Retrieve all items
@router.get("/{model-name}s", response_model=List[{ModelName}])
def get_all_{model_name}s(db: NoSqlDb = Depends(get_db)):
# def get_all_{model_name}s(user: dict = Depends(get_current_user), db: NoSqlDb = Depends(get_db)):
    logger.info("Received request to retrieve all {model_name}")
    return db.get_all_items("{model_name}")

# Retrieve a single item
@router.get("/{model-name}/{id}", response_model={ModelName})
def get_{model_name}(id: str, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to retrieve {model_name} with id: {id}")
    item = db.get_item("{model_name}", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved {model_name}: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/{model-name}/{id}", response_model={ModelName})
def update_{model_name}(id: str, updated_item: {ModelName}, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("{model_name}", id)
    logger.info(f"Received request to update {model_name} with id {id}: {updated_item}")
    if not item:
        logger.warning(f"{ModelName} with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("{model_name}", id, updated_item.dict())
    return db.get_item("{model_name}", id)

# Delete an item
@router.delete("/{model-name}/{id}")
def delete_{model_name}(id: str, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("{model_name}", id)
    if not item:
        logger.warning(f"{ModelName} with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("{model_name}", id)
    return {"message": "Deleted successfully"}
