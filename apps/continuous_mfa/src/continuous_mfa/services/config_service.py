import logging
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from continuous_mfa.models.config import Config

logger = logging.getLogger(__name__)

# write - Create an item
def create_config(item: Config, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_config called==============")

    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - if db: ...
    db.insert_item("config", item_id, new_item)
    logger.info(f"Config created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Config created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - get all items
def get_all_config(db: NoSqlDb, user: dict):
    logger.info("===============get_all_config called==============")
    return db.get_all_items("config")

# read - get an item
def get_config(id: str, db: NoSqlDb, user: dict):
    logger.info("===============get_config called==============")
    logger.info(f"Received request to retrieve config with id: {id}")
    item = db.get_item("config", id)
    return item

# write - update an item (without modifying ID)
def update_config(id: str, new_item: Config, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============update_config called==============")
    logger.info(new_item)
    db.update_item("config", id, new_item.model_dump())
    return db.get_item("config", id)

# write - delete an item
def delete_config(id: str, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============delete_config called==============")
    logger.info(f"Received request to delete config with id {id}")
    item = db.get_item("config", id)
    if not item:
        logger.warning(f"Config with id {id} not found")
        return None
    db.delete_item("config", id)
    return item