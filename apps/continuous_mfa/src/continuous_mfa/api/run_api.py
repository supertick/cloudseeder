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
from continuous_mfa.models.run import Run
from typing import Dict
from auth.factory import get_auth_provider
from continuous_mfa.auth_util import require_role, no_role_required
from continuous_mfa.config import config_provider
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

    return get_queue_client(name="run", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/run", response_model=Run)
def create_run(item: Run, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to create: {item}")
    ret = safe_invoke("continuous_mfa.services.run_service", "create_run", [item, db, q, user])
    return ret

# read - Retrieve all items
@router.get("/runs", response_model=List[Run])
def get_all_runs(db: NoSqlDb = Depends(get_db_provider),
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug("Received request to retrieve all run")
    ret = safe_invoke("continuous_mfa.services.run_service", "get_all_run", [db, user])
    return ret

# read - Retrieve a single item
@router.get("/run/{id}", response_model=Run)
def get_run(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to retrieve run with id: {id}")
    ret =safe_invoke("continuous_mfa.services.run_service", "get_run", [id, db, user])
    if not ret:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved run: {ret}")
    return ret

# write - Update an item (without modifying ID)
@router.put("/run/{id}", response_model=Run)
def update_run(id: str, 
                        updated_item: Run, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("run", id)
    logger.debug(f"Received request to update run with id {id}: {updated_item}")
    ret = safe_invoke("continuous_mfa.services.run_service", "update_run", [id, updated_item, db, q, user])
    if not item:
        logger.warning(f"Run with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret

# write - Delete an item
@router.delete("/run/{id}")
def delete_run(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to delete run with id {id}")
    ret = safe_invoke("continuous_mfa.services.run_service", "delete_run", [id, db, q, user])
    if not ret:
        logger.warning(f"Run with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret
