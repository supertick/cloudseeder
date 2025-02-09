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
from continuous_mfa.models.report import Report
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

    return get_queue_client(name="report", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/report", response_model=Report)
def create_report(item: Report, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to create: {item}")
    ret = safe_invoke("continuous_mfa.services.report_service", "create_report", [item, db, q, user])
    return ret

# read - Retrieve all items
@router.get("/reports", response_model=List[Report])
def get_all_reports(db: NoSqlDb = Depends(get_db_provider),
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug("Received request to retrieve all report")
    ret = safe_invoke("continuous_mfa.services.report_service", "get_all_report", [db, user])
    return ret

# read - Retrieve a single item
@router.get("/report/{id}", response_model=Report)
def get_report(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to retrieve report with id: {id}")
    ret =safe_invoke("continuous_mfa.services.report_service", "get_report", [id, db, user])
    if not ret:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved report: {ret}")
    return ret

# write - Update an item (without modifying ID)
@router.put("/report/{id}", response_model=Report)
def update_report(id: str, 
                        updated_item: Report, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("report", id)
    logger.debug(f"Received request to update report with id {id}: {updated_item}")
    ret = safe_invoke("continuous_mfa.services.report_service", "update_report", [id, updated_item, db, q, user])
    if not item:
        logger.warning(f"Report with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret

# write - Delete an item
@router.delete("/report/{id}")
def delete_report(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to delete report with id {id}")
    ret = safe_invoke("continuous_mfa.services.report_service", "delete_report", [id, db, q, user])
    if not ret:
        logger.warning(f"Report with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret
