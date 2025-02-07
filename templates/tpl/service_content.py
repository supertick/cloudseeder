import logging
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from {app_name}.models.{model_name} import {ModelName}

logger = logging.getLogger(__name__)

# write - Create an item
def create_{model_name}(item: {ModelName}, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_{model_name} called==============")

    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - if db: ...
    db.insert_item("{model_name}", item_id, new_item)
    logger.info(f"{ModelName} created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: {ModelName} created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - get all items
def get_all_{model_name}(db: NoSqlDb, user: dict):
    logger.info("===============get_all_{model_name} called==============")
    return db.get_all_items("{model_name}")

# read - get an item
def get_{model_name}(id: str, db: NoSqlDb, user: dict):
    logger.info("===============get_{model_name} called==============")
    logger.info(f"Received request to retrieve {model_name} with id: {id}")
    item = db.get_item("{model_name}", id)
    return item

# write - update an item (without modifying ID)
def update_{model_name}(id: str, new_item: {ModelName}, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============update_{model_name} called==============")
    logger.info(new_item)
    db.update_item("{model_name}", id, new_item.model_dump())
    return db.get_item("{model_name}", id)

# write - delete an item
def delete_{model_name}(id: str, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============delete_{model_name} called==============")
    logger.info(f"Received request to delete {model_name} with id {id}")
    item = db.get_item("{model_name}", id)
    if not item:
        logger.warning(f"{ModelName} with id {id} not found")
        return None
    db.delete_item("{model_name}", id)
    return item