import logging
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from {app_name}.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database, get_db
from queues.factory import get_queue_client
from queues.interface import QueueClient
from {app_name}.models.{model_name} import {ModelName}
from typing import Dict
from auth.factory import get_auth_provider
from {app_name}.auth_util import require_role, no_role_required
from {app_name}.config import config_provider
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

    return get_queue_client(name="{model_name}", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/{model-name}", response_model={ModelName})
def create_{model_name}(item: {ModelName}, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to create: {item}")
    ret = safe_invoke("{app_name}.services.{model_name}_service", "create_{model_name}", [item, db, q, user])
    return ret

# read - Retrieve all items
@router.get("/{model-name}s", response_model=List[{ModelName}])
def get_all_{model_name}s(db: NoSqlDb = Depends(get_db_provider),
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug("Received request to retrieve all {model_name}")
    ret = safe_invoke("{app_name}.services.{model_name}_service", "get_all_{model_name}", [db, user])
    return ret

# read - Retrieve a single item
@router.get("/{model-name}/{id}", response_model={ModelName})
def get_{model_name}(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to retrieve {model_name} with id: {id}")
    ret =safe_invoke("{app_name}.services.{model_name}_service", "get_{model_name}", [id, db, user])
    if not ret:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved {model_name}: {ret}")
    return ret

# write - Update an item (without modifying ID)
@router.put("/{model-name}/{id}", response_model={ModelName})
def update_{model_name}(id: str, 
                        updated_item: {ModelName}, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("{model_name}", id)
    logger.debug(f"Received request to update {model_name} with id {id}: {updated_item}")
    ret = safe_invoke("{app_name}.services.{model_name}_service", "update_{model_name}", [id, updated_item, db, q, user])
    if not item:
        logger.warning(f"{ModelName} with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret

# write - Delete an item
@router.delete("/{model-name}/{id}")
def delete_{model_name}(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to delete {model_name} with id {id}")
    ret = safe_invoke("{app_name}.services.{model_name}_service", "delete_{model_name}", [id, db, q, user])
    if not ret:
        logger.warning(f"{ModelName} with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret
