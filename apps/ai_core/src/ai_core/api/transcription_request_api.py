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
from ai_core.models.transcription_request import TranscriptionRequest
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

    return get_queue_client(name="transcription_request", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/transcription-request", response_model=TranscriptionRequest)
def create_transcription_request(item: TranscriptionRequest, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to create: {item}")
    ret = safe_invoke("ai_core.services.transcription_request_service", "create_transcription_request", [item, db, q, user])
    return ret

# read - Retrieve all items
@router.get("/transcription-requests", response_model=List[TranscriptionRequest])
def get_all_transcription_requests(db: NoSqlDb = Depends(get_db_provider),
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug("Received request to retrieve all transcription_request")
    ret = safe_invoke("ai_core.services.transcription_request_service", "get_all_transcription_request", [db, user])
    return ret

# read - Retrieve a single item
@router.get("/transcription-request/{id}", response_model=TranscriptionRequest)
def get_transcription_request(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to retrieve transcription_request with id: {id}")
    ret =safe_invoke("ai_core.services.transcription_request_service", "get_transcription_request", [id, db, user])
    if not ret:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved transcription_request: {ret}")
    return ret

# write - Update an item (without modifying ID)
@router.put("/transcription-request/{id}", response_model=TranscriptionRequest)
def update_transcription_request(id: str, 
                        updated_item: TranscriptionRequest, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("transcription_request", id)
    logger.debug(f"Received request to update transcription_request with id {id}: {updated_item}")
    ret = safe_invoke("ai_core.services.transcription_request_service", "update_transcription_request", [id, updated_item, db, q, user])
    if not item:
        logger.warning(f"TranscriptionRequest with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret

# write - Delete an item
@router.delete("/transcription-request/{id}")
def delete_transcription_request(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to delete transcription_request with id {id}")
    ret = safe_invoke("ai_core.services.transcription_request_service", "delete_transcription_request", [id, db, q, user])
    if not ret:
        logger.warning(f"TranscriptionRequest with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret
