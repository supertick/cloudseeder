import logging
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from continuous_mfa.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database, get_db
from queues.factory import get_queue_client
from queues.interface import QueueClient
from continuous_mfa.models.input import Input, Input
from typing import Dict
from auth.factory import get_auth_provider
from continuous_mfa.auth_util import require_role, no_role_required
from continuous_mfa.config import config_provider


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

auth = get_auth_provider(config_provider)
security = HTTPBearer()

def get_db_provider() -> NoSqlDb:
    return get_database(config_provider)

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

    return get_queue_client(name="input", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/input", response_model=Input)
def create_input(item: Input, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to create: {item}")
    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database
    # FIXME - if db: ...
    db.insert_item("input", item_id, new_item)
    logger.info(f"Input created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Input created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - Retrieve all items
@router.get("/inputs", response_model=List[Input])
def get_all_inputs(db: NoSqlDb = Depends(get_db_provider), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info("Received request to retrieve all input")
    return db.get_all_items("input")

# read - Retrieve a single item
@router.get("/input/{id}", response_model=Input)
def get_input(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to retrieve input with id: {id}")
    item = db.get_item("input", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved input: {item}")
    return item

# write - Update an item (without modifying ID)
@router.put("/input/{id}", response_model=Input)
def update_input(id: str, 
                        updated_item: Input, db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("input", id)
    logger.info(f"Received request to update input with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Input with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("input", id, updated_item.model_dump())
    return db.get_item("input", id)

# write - Delete an item
@router.delete("/input/{id}")
def delete_input(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("input", id)
    if not item:
        logger.warning(f"Input with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("input", id)
    return {"message": "Deleted successfully"}
