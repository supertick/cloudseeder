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
from continuous_mfa.models.upload_file_content import UploadFileContent
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

    return get_queue_client(name="upload_file_content", queue_type="local", **q_params)  # Pass to factory



# write - Create an item
@router.post("/upload-file-content", response_model=UploadFileContent)
def create_upload_file_content(item: UploadFileContent, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to create: {item}")
    ret = safe_invoke("continuous_mfa.services.upload_file_content_service", "create_upload_file_content", [item, db, q, user])
    return ret

# read - Retrieve all items
@router.get("/upload-file-contents", response_model=List[UploadFileContent])
def get_all_upload_file_contents(db: NoSqlDb = Depends(get_db_provider),
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug("Received request to retrieve all upload_file_content")
    ret = safe_invoke("continuous_mfa.services.upload_file_content_service", "get_all_upload_file_content", [db, user])
    return ret

# read - Retrieve a single item
@router.get("/upload-file-content/{id}", response_model=UploadFileContent)
def get_upload_file_content(id: str, 
                     db: NoSqlDb = Depends(get_db_provider), 
                     user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to retrieve upload_file_content with id: {id}")
    ret =safe_invoke("continuous_mfa.services.upload_file_content_service", "get_upload_file_content", [id, db, user])
    if not ret:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved upload_file_content: {ret}")
    return ret

# write - Update an item (without modifying ID)
@router.put("/upload-file-content/{id}", response_model=UploadFileContent)
def update_upload_file_content(id: str, 
                        updated_item: UploadFileContent, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    item = db.get_item("upload_file_content", id)
    logger.debug(f"Received request to update upload_file_content with id {id}: {updated_item}")
    ret = safe_invoke("continuous_mfa.services.upload_file_content_service", "update_upload_file_content", [id, updated_item, db, q, user])
    if not item:
        logger.warning(f"UploadFileContent with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret

# write - Delete an item
@router.delete("/upload-file-content/{id}")
def delete_upload_file_content(id: str, 
                        db: NoSqlDb = Depends(get_db_provider), 
                        q: QueueClient = Depends(get_queue), 
                        user: dict = Depends(require_role([]) if settings.auth_enabled else no_role_required)):
    logger.debug(f"Received request to delete upload_file_content with id {id}")
    ret = safe_invoke("continuous_mfa.services.upload_file_content_service", "delete_upload_file_content", [id, db, q, user])
    if not ret:
        logger.warning(f"UploadFileContent with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return ret
