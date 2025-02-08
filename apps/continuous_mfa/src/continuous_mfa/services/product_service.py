import logging
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from continuous_mfa.models.product import Product

logger = logging.getLogger(__name__)

# write - Create an item
def create_product(item: Product, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_product called==============")

    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - if db: ...
    db.insert_item("product", item_id, new_item)
    logger.info(f"Product created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: Product created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - get all items
def get_all_product(db: NoSqlDb, user: dict):
    logger.info("===============get_all_product called==============")
    return db.get_all_items("product")

# read - get an item
def get_product(id: str, db: NoSqlDb, user: dict):
    logger.info("===============get_product called==============")
    logger.info(f"Received request to retrieve product with id: {id}")
    item = db.get_item("product", id)
    return item

# write - update an item (without modifying ID)
def update_product(id: str, new_item: Product, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============update_product called==============")
    logger.info(new_item)
    db.update_item("product", id, new_item.model_dump())
    return db.get_item("product", id)

# write - delete an item
def delete_product(id: str, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============delete_product called==============")
    logger.info(f"Received request to delete product with id {id}")
    item = db.get_item("product", id)
    if not item:
        logger.warning(f"Product with id {id} not found")
        return None
    db.delete_item("product", id)
    return item