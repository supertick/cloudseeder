import logging
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from continuous_mfa.models.run import Run

logger = logging.getLogger(__name__)

# write - Create an item
def create_run(item: Run, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_run called==============")

    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - if db: ...
    db.insert_item("run", item_id, new_item)
    logger.info(f"Run created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Run created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - get all items
def get_all_run(db: NoSqlDb, user: dict):
    logger.info("===============get_all_run called==============")
    return db.get_all_items("run")

# read - get an item
def get_run(id: str, db: NoSqlDb, user: dict):
    logger.info("===============get_run called==============")
    logger.info(f"Received request to retrieve run with id: {id}")
    item = db.get_item("run", id)
    return item

# write - update an item (without modifying ID)
def update_run(id: str, new_item: Run, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============update_run called==============")
    logger.info(new_item)
    db.update_item("run", id, new_item.model_dump())
    return db.get_item("run", id)

# write - delete an item
def delete_run(id: str, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============delete_run called==============")
    logger.info(f"Received request to delete run with id {id}")
    item = db.get_item("run", id)
    if not item:
        logger.warning(f"Run with id {id} not found")
        return None
    db.delete_item("run", id)
    return item