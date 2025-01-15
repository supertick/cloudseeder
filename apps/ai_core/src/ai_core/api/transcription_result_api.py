import logging
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from ai_core.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from queues.factory import get_queue_client
from queues.interface import QueueClient
from ai_core.models.transcription_result import Transcription_result, Transcription_result
from typing import Dict
from auth.factory import get_auth_provider
from ..auth_util import require_role
    
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

    return get_queue_client(name="transcription_result", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/transcription-result", response_model=Transcription_result)
def create_transcription_result(item: Transcription_result, db: NoSqlDb = Depends(get_db), q: QueueClient = Depends(get_queue), user: dict = Depends(require_role([]))):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database
    # FIXME - if db: ...
    db.insert_item("transcription_result", item_id, new_item)
    logger.info(f"Transcription_result created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Transcription_result created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - Retrieve all items
@router.get("/transcription-results", response_model=List[Transcription_result])
def get_all_transcription_results(db: NoSqlDb = Depends(get_db), user: dict = Depends(require_role([]))):
    logger.info("Received request to retrieve all transcription_result")
    return db.get_all_items("transcription_result")

# read - Retrieve a single item
@router.get("/transcription-result/{id}", response_model=Transcription_result)
def get_transcription_result(id: str, db: NoSqlDb = Depends(get_db), user: dict = Depends(require_role([]))):
    logger.info(f"Received request to retrieve transcription_result with id: {id}")
    item = db.get_item("transcription_result", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved transcription_result: {item}")
    return item

# write - Update an item (without modifying ID)
@router.put("/transcription-result/{id}", response_model=Transcription_result)
def update_transcription_result(id: str, updated_item: Transcription_result, db: NoSqlDb = Depends(get_db), q: QueueClient = Depends(get_queue), user: dict = Depends(require_role([]))):
    item = db.get_item("transcription_result", id)
    logger.info(f"Received request to update transcription_result with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Transcription_result with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("transcription_result", id, updated_item.model_dump())
    return db.get_item("transcription_result", id)

# write - Delete an item
@router.delete("/transcription-result/{id}")
def delete_transcription_result(id: str, db: NoSqlDb = Depends(get_db), q: QueueClient = Depends(get_queue), user: dict = Depends(require_role([]))):
    item = db.get_item("transcription_result", id)
    if not item:
        logger.warning(f"Transcription_result with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("transcription_result", id)
    return {"message": "Deleted successfully"}
