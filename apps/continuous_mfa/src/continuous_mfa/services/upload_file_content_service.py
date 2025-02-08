import logging
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from continuous_mfa.models.upload_file_content import UploadFileContent

logger = logging.getLogger(__name__)

# write - Create an item
def create_upload_file_content(item: UploadFileContent, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_upload_file_content called==============")

    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - if db: ...
    db.insert_item("upload_file_content", item_id, new_item)
    logger.info(f"UploadFileContent created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: UploadFileContent created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - get all items
def get_all_upload_file_content(db: NoSqlDb, user: dict):
    logger.info("===============get_all_upload_file_content called==============")
    return db.get_all_items("upload_file_content")

# read - get an item
def get_upload_file_content(id: str, db: NoSqlDb, user: dict):
    logger.info("===============get_upload_file_content called==============")
    logger.info(f"Received request to retrieve upload_file_content with id: {id}")
    item = db.get_item("upload_file_content", id)
    return item

# write - update an item (without modifying ID)
def update_upload_file_content(id: str, new_item: UploadFileContent, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============update_upload_file_content called==============")
    logger.info(new_item)
    db.update_item("upload_file_content", id, new_item.model_dump())
    return db.get_item("upload_file_content", id)

# write - delete an item
def delete_upload_file_content(id: str, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============delete_upload_file_content called==============")
    logger.info(f"Received request to delete upload_file_content with id {id}")
    item = db.get_item("upload_file_content", id)
    if not item:
        logger.warning(f"UploadFileContent with id {id} not found")
        return None
    db.delete_item("upload_file_content", id)
    return item