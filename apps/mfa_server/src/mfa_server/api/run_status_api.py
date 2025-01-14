import logging
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import uuid
from mfa_server.config import settings 
from database.interface import NoSqlDb
from database.factory import get_database
from queues.factory import get_queue_client
from queues.interface import QueueClient
from mfa_server.models.run_status import Run_status, Run_status
from typing import Dict
from auth.factory import get_auth_provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

auth = get_auth_provider()
security = HTTPBearer()

# Authentication dependency - FIXME probably not good to have this replicated in every model
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Get current authenticated user from token."""
    token = credentials.credentials
    user = auth.get_user(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user

# Role-based access control (RBAC) dependency
def require_role(required_roles: List[str]):
    """Dependency factory for role-based access control."""
    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in required_roles:
            raise HTTPException(status_code=403, detail="Access denied: Insufficient permissions")
        return user
    return role_checker


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

    return get_queue_client(name="Run_status", queue_type="local", **q_params)  # Pass to factory



# Create an item
@router.post("/run-status", response_model=Run_status)
def create_run_status(item: Run_status, db: NoSqlDb = Depends(get_db), q: QueueClient = Depends(get_queue)):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("run_status", item_id, new_item)
    logger.info(f"Run_status created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Run_status created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# Retrieve all items
@router.get("/run-statuss", response_model=List[Run_status])
def get_all_run_statuss(db: NoSqlDb = Depends(get_db)):
# def get_all_run_statuss(user: dict = Depends(get_current_user), db: NoSqlDb = Depends(get_db)):
    logger.info("Received request to retrieve all run_status")
    return db.get_all_items("run_status")

# Retrieve a single item
@router.get("/run-status/{id}", response_model=Run_status)
def get_run_status(id: str, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to retrieve run_status with id: {id}")
    item = db.get_item("run_status", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved run_status: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/run-status/{id}", response_model=Run_status)
def update_run_status(id: str, updated_item: Run_status, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("run_status", id)
    logger.info(f"Received request to update run_status with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Run_status with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("run_status", id, updated_item.dict())
    return db.get_item("run_status", id)

# Delete an item
@router.delete("/run-status/{id}")
def delete_run_status(id: str, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("run_status", id)
    if not item:
        logger.warning(f"Run_status with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("run_status", id)
    return {"message": "Deleted successfully"}
