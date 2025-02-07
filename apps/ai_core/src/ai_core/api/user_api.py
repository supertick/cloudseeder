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
from ai_core.models.user import User
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

    return get_queue_client(name="user", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/user", response_model=User)
def create_user(item: User, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to create: {item}")
    ret = safe_invoke("ai_core.services.user_service", "create_user", [item, db, q, user])
    return ret

# read - Retrieve all items
@router.get("/users", response_model=List[User])
def get_all_users(db: NoSqlDb = Depends(get_db_provider),
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug("Received request to retrieve all user")
    ret = safe_invoke("ai_core.services.user_service", "get_all_user", [db, user])
    return ret

# read - Retrieve a single item
@router.get("/user/{id}", response_model=User)
def get_user(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to retrieve user with id: {id}")
    ret =safe_invoke("ai_core.services.user_service", "get_user", [id, db, user])
    if not ret:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved user: {ret}")
    return ret

# write - Update an item (without modifying ID)
@router.put("/user/{id}", response_model=User)
def update_user(id: str, 
                        updated_item: User, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("user", id)
    logger.debug(f"Received request to update user with id {id}: {updated_item}")
    ret = safe_invoke("ai_core.services.user_service", "update_user", [id, updated_item, db, q, user])
    if not item:
        logger.warning(f"User with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret

# write - Delete an item
@router.delete("/user/{id}")
def delete_user(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to delete user with id {id}")
    ret = safe_invoke("ai_core.services.user_service", "delete_user", [id, db, q, user])
    if not ret:
        logger.warning(f"User with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret
