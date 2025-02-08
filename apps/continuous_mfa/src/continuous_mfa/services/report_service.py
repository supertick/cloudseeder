import logging
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from continuous_mfa.models.report import Report

logger = logging.getLogger(__name__)

# write - Create an item
def create_report(item: Report, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_report called==============")

    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - if db: ...
    db.insert_item("report", item_id, new_item)
    logger.info(f"Report created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Report created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - get all items
def get_all_report(db: NoSqlDb, user: dict):
    logger.info("===============get_all_report called==============")
    return db.get_all_items("report")

# read - get an item
def get_report(id: str, db: NoSqlDb, user: dict):
    logger.info("===============get_report called==============")
    logger.info(f"Received request to retrieve report with id: {id}")
    item = db.get_item("report", id)
    return item

# write - update an item (without modifying ID)
def update_report(id: str, new_item: Report, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============update_report called==============")
    logger.info(new_item)
    db.update_item("report", id, new_item.model_dump())
    return db.get_item("report", id)

# write - delete an item
def delete_report(id: str, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============delete_report called==============")
    logger.info(f"Received request to delete report with id {id}")
    item = db.get_item("report", id)
    if not item:
        logger.warning(f"Report with id {id} not found")
        return None
    db.delete_item("report", id)
    return item