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
from ai_core.models.transcription_result import TranscriptionResult
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

    return get_queue_client(name="transcription_result", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/transcription-result", response_model=TranscriptionResult)
def create_transcription_result(item: TranscriptionResult, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to create: {item}")
    ret = safe_invoke("ai_core.services.transcription_result_service", "create_transcription_result", [item, db, q, user])
    return ret

# read - Retrieve all items
@router.get("/transcription-results", response_model=List[TranscriptionResult])
def get_all_transcription_results(db: NoSqlDb = Depends(get_db_provider), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info("Received request to retrieve all transcription_result")
    ret = safe_invoke("ai_core.services.transcription_result_service", "get_all_transcription_result", [db, q, user])
    return db.get_all_items("transcription_result")

# read - Retrieve a single item
@router.get("/transcription-result/{id}", response_model=TranscriptionResult)
def get_transcription_result(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to retrieve transcription_result with id: {id}")
    safe_invoke("ai_core.services.transcription_result_service", "get_transcription_result", [id, db, q, user])
    item = db.get_item("transcription_result", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved transcription_result: {item}")
    return item

# write - Update an item (without modifying ID)
@router.put("/transcription-result/{id}", response_model=TranscriptionResult)
def update_transcription_result(id: str, 
                        updated_item: TranscriptionResult, db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("transcription_result", id)
    logger.info(f"Received request to update transcription_result with id {id}: {updated_item}")
    ret = safe_invoke("ai_core.services.transcription_result_service", "update_transcription_result", [id, updated_item, db, q, user])
    if not item:
        logger.warning(f"TranscriptionResult with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("transcription_result", id, updated_item.model_dump())
    return db.get_item("transcription_result", id)

# write - Delete an item
@router.delete("/transcription-result/{id}")
def delete_transcription_result(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("transcription_result", id)
    if not item:
        logger.warning(f"TranscriptionResult with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    ret = safe_invoke("ai_core.services.transcription_result_service", "delete_transcription_result", [id, db, q, user])
    db.delete_item("transcription_result", id)
    return {"message": "Deleted successfully"}
