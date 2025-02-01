import logging
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from ai_core.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database, get_db
from queues.factory import get_queue_client
from queues.interface import QueueClient
from ai_core.models.config import Config
from typing import Dict
from auth.factory import get_auth_provider
from ai_core.auth_util import require_role, no_role_required
from ai_core.config import config_provider
from ai_core.invoker import safe_invoke


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

    return get_queue_client(name="config", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/config", response_model=Config)
def create_config(item: Config, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to create: {item}")
    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    ret = safe_invoke("ai_core.services.config_service", "create_config", [new_item, db, q, user])

    # FIXME - if db: ...
    db.insert_item("config", item_id, new_item)
    logger.info(f"Config created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Config created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - Retrieve all items
@router.get("/configs", response_model=List[Config])
def get_all_configs(db: NoSqlDb = Depends(get_db_provider), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info("Received request to retrieve all config")
    ret = safe_invoke("ai_core.services.config_service", "get_all_config", [db, q, user])
    return db.get_all_items("config")

# read - Retrieve a single item
@router.get("/config/{id}", response_model=Config)
def get_config(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to retrieve config with id: {id}")
    safe_invoke("ai_core.services.config_service", "get_config", [id, db, q, user])
    item = db.get_item("config", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved config: {item}")
    return item

# write - Update an item (without modifying ID)
@router.put("/config/{id}", response_model=Config)
def update_config(id: str, 
                        updated_item: Config, db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("config", id)
    logger.info(f"Received request to update config with id {id}: {updated_item}")
    ret = safe_invoke("ai_core.services.config_service", "update_config", [id, updated_item, db, q, user])
    if not item:
        logger.warning(f"Config with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("config", id, updated_item.model_dump())
    return db.get_item("config", id)

# write - Delete an item
@router.delete("/config/{id}")
def delete_config(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("config", id)
    if not item:
        logger.warning(f"Config with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    ret = safe_invoke("ai_core.services.config_service", "delete_config", [id, db, q, user])
    db.delete_item("config", id)
    return {"message": "Deleted successfully"}
