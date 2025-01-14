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
from mfa_server.models.run import Run, Run
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

    return get_queue_client(name="Run", queue_type="local", **q_params)  # Pass to factory



# Create an item
@router.post("/run", response_model=Run)
def create_run(item: Run, db: NoSqlDb = Depends(get_db), q: QueueClient = Depends(get_queue)):
    logger.info(f"Received request to create: {item}")
    item_id = str(uuid.uuid4())  # Generate a new UUID
    new_item = item.dict()
    new_item["id"] = item_id  # Store UUID in the database
    db.insert_item("run", item_id, new_item)
    logger.info(f"Run created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Run created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# Retrieve all items
@router.get("/runs", response_model=List[Run])
def get_all_runs(db: NoSqlDb = Depends(get_db)):
# def get_all_runs(user: dict = Depends(get_current_user), db: NoSqlDb = Depends(get_db)):
    logger.info("Received request to retrieve all run")
    return db.get_all_items("run")

# Retrieve a single item
@router.get("/run/{id}", response_model=Run)
def get_run(id: str, db: NoSqlDb = Depends(get_db)):
    logger.info(f"Received request to retrieve run with id: {id}")
    item = db.get_item("run", id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Retrieved run: {item}")
    return item

# Update an item (without modifying ID)
@router.put("/run/{id}", response_model=Run)
def update_run(id: str, updated_item: Run, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("run", id)
    logger.info(f"Received request to update run with id {id}: {updated_item}")
    if not item:
        logger.warning(f"Run with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.update_item("run", id, updated_item.dict())
    return db.get_item("run", id)

# Delete an item
@router.delete("/run/{id}")
def delete_run(id: str, db: NoSqlDb = Depends(get_db)):
    item = db.get_item("run", id)
    if not item:
        logger.warning(f"Run with id {id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete_item("run", id)
    return {"message": "Deleted successfully"}
