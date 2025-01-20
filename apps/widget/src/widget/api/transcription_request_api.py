import logging
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from widget.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database, get_db
from queues.factory import get_queue_client
from queues.interface import QueueClient
from widget.models.transcription_request import Transcription_request, Transcription_request
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

    return get_queue_client(name="transcription_request", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/transcription-request", response_model=Transcription_request)
def create_transcription_request(item: Transcription_request, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to create: {item}")
    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database
    # FIXME - if db: ...
    db.insert_item("transcription_request", item_id, new_item)
    logger.info(f"Transcription_request created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Transcription_request created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - Retrieve all items
@router.get("/transcription-requests", response_model=List[Transcription_request])
def get_all_transcription_requests(db: NoSqlDb = Depends(get_db_provider), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info("Received request to retrieve all transcription_request")
    return db.get_all_items("transcription_request")

# read - Retrieve a single item
@router.get("/transcription-request/{id}", response_model=Transcription_request)
def get_transcription_request(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.info(f"Received request to retrieve transcription_request with id: {id}")
    item = db.get_item("transcription_request", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved transcription_request: {item}")
    return item

# write - Update an item (without modifying ID)
@router.put("/transcription-request/{id}", response_model=Transcription_request)
def update_transcription_request(id: str, 
                        updated_item: Transcription_request, db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("transcription_request", id)
    logger.info(f"Received request to update transcription_request with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Transcription_request with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("transcription_request", id, updated_item.model_dump())
    return db.get_item("transcription_request", id)

# write - Delete an item
@router.delete("/transcription-request/{id}")
def delete_transcription_request(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("transcription_request", id)
    if not item:
        logger.warning(f"Transcription_request with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("transcription_request", id)
    return {"message": "Deleted successfully"}
