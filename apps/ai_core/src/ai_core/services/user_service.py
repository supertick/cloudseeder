import logging
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from ai_core.models.user import User

logger = logging.getLogger(__name__)

# write - Create an item
def create_user(item: User, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_user called==============")

    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - if db: ...
    db.insert_item("user", item_id, new_item)
    logger.info(f"User created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: User created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - get all items
def get_all_user(db: NoSqlDb, user: dict):
    logger.info("===============get_all_user called==============")
    return db.get_all_items("user")

# read - get an item
def get_user(id: str, db: NoSqlDb, user: dict):
    logger.info("===============get_user called==============")
    logger.info(f"Received request to retrieve user with id: {id}")
    item = db.get_item("user", id)
    return item

# write - update an item (without modifying ID)
def update_user(id: str, new_item: User, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============update_user called==============")
    logger.info(new_item)
    db.update_item("user", id, new_item.model_dump())
    return db.get_item("user", id)

# write - delete an item
def delete_user(id: str, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============delete_user called==============")
    logger.info(f"Received request to delete user with id {id}")
    item = db.get_item("user", id)
    if not item:
        logger.warning(f"User with id {id} not found")
        return None
    db.delete_item("user", id)
    return item