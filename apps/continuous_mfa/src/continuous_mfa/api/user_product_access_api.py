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
from continuous_mfa.models.user_product_access import UserProductAccess
from typing import Dict
from auth.factory import get_auth_provider
from continuous_mfa.auth_util import require_role, no_role_required
from continuous_mfa.config import config_provider
from continuous_mfa.invoker import safe_invoke


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
@router.post("/user-product-access", response_model=UserProductAccess)
def create_user_product_access(item: UserProductAccess, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to create: {item}")
    ret = safe_invoke("continuous_mfa.services.user_product_access_service", "create_user_product_access", [item, db, q, user])
    return ret

# read - Retrieve all items
@router.get("/user-product-accesss", response_model=List[UserProductAccess])
def get_all_user_product_accesss(db: NoSqlDb = Depends(get_db_provider),
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug("Received request to retrieve all user_product_access")
    ret = safe_invoke("continuous_mfa.services.user_product_access_service", "get_all_user_product_access", [db, user])
    return ret

# read - Retrieve a single item
@router.get("/user-product-access/{id}", response_model=UserProductAccess)
def get_user_product_access(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to retrieve user_product_access with id: {id}")
    ret =safe_invoke("continuous_mfa.services.user_product_access_service", "get_user_product_access", [id, db, user])
    if not ret:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved user_product_access: {ret}")
    return ret

# write - Update an item (without modifying ID)
@router.put("/user-product-access/{id}", response_model=UserProductAccess)
def update_user_product_access(id: str, 
                        updated_item: UserProductAccess, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("user_product_access", id)
    logger.debug(f"Received request to update user_product_access with id {id}: {updated_item}")
    ret = safe_invoke("continuous_mfa.services.user_product_access_service", "update_user_product_access", [id, updated_item, db, q, user])
    if not item:
        logger.warning(f"UserProductAccess with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret

# write - Delete an item
@router.delete("/user-product-access/{id}")
def delete_user_product_access(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to delete user_product_access with id {id}")
    ret = safe_invoke("continuous_mfa.services.user_product_access_service", "delete_user_product_access", [id, db, q, user])
    if not ret:
        logger.warning(f"UserProductAccess with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret
