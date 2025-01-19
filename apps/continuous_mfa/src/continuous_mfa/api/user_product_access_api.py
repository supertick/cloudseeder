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
from continuous_mfa.models.user_product_access import User_product_access, User_product_access
from typing import Dict
from auth.factory import get_auth_provider
from ..auth_util import require_role, no_role_required
from ..config import config_provider


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

    return get_queue_client(name="user_product_access", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/user-product-access", response_model=User_product_access)
def create_user_product_access(item: User_product_access, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to create: {item}")
    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database
    # FIXME - if db: ...
    db.insert_item("user_product_access", item_id, new_item)
    logger.info(f"User_product_access created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: User_product_access created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - Retrieve all items
@router.get("/user-product-accesss", response_model=List[User_product_access])
def get_all_user_product_accesss(db: NoSqlDb = Depends(get_db_provider), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info("Received request to retrieve all user_product_access")
    return db.get_all_items("user_product_access")

# read - Retrieve a single item
@router.get("/user-product-access/{id}", response_model=User_product_access)
def get_user_product_access(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to retrieve user_product_access with id: {id}")
    item = db.get_item("user_product_access", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved user_product_access: {item}")
    return item

# write - Update an item (without modifying ID)
@router.put("/user-product-access/{id}", response_model=User_product_access)
def update_user_product_access(id: str, 
                        updated_item: User_product_access, db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("user_product_access", id)
    logger.info(f"Received request to update user_product_access with id {id}: {updated_item}")
    if not item:
        logger.warning(f"User_product_access with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("user_product_access", id, updated_item.model_dump())
    return db.get_item("user_product_access", id)

# write - Delete an item
@router.delete("/user-product-access/{id}")
def delete_user_product_access(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("user_product_access", id)
    if not item:
        logger.warning(f"User_product_access with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("user_product_access", id)
    return {"message": "Deleted successfully"}
