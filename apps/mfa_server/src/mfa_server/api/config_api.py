import logging
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from mfa_server.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from queues.factory import get_queue_client
from queues.interface import QueueClient
from mfa_server.models.config import Config, Config
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

    return get_queue_client(name="config", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/config", response_model=Config)
def create_config(item: Config, db: NoSqlDb = Depends(get_db), q: QueueClient = Depends(get_queue), user: dict = Depends(require_role([]))):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database
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
def get_all_configs(db: NoSqlDb = Depends(get_db), user: dict = Depends(require_role([]))):
# def get_all_configs(user: dict = Depends(get_current_user), db: NoSqlDb = Depends(get_db)):
    logger.info("Received request to retrieve all config")
    return db.get_all_items("config")

# read - Retrieve a single item
@router.get("/config/{id}", response_model=Config)
def get_config(id: str, db: NoSqlDb = Depends(get_db), user: dict = Depends(require_role([]))):
    logger.info(f"Received request to retrieve config with id: {id}")
    item = db.get_item("config", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved config: {item}")
    return item

# write - Update an item (without modifying ID)
@router.put("/config/{id}", response_model=Config)
def update_config(id: str, updated_item: Config, db: NoSqlDb = Depends(get_db), q: QueueClient = Depends(get_queue), user: dict = Depends(require_role([]))):
    item = db.get_item("config", id)
    logger.info(f"Received request to update config with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Config with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("config", id, updated_item.model_dump())
    return db.get_item("config", id)

# write - Delete an item
@router.delete("/config/{id}")
def delete_config(id: str, db: NoSqlDb = Depends(get_db), q: QueueClient = Depends(get_queue), user: dict = Depends(require_role([]))):
    item = db.get_item("config", id)
    if not item:
        logger.warning(f"Config with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("config", id)
    return {"message": "Deleted successfully"}
