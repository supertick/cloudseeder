import logging
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from ai_core.models.transcription_request import TranscriptionRequest

logger = logging.getLogger(__name__)

# write - Create an item
def create_transcription_request(item: TranscriptionRequest, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_transcription_request called==============")

    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - if db: ...
    db.insert_item("transcription_request", item_id, new_item)
    logger.info(f"TranscriptionRequest created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: TranscriptionRequest created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - get all items
def get_all_transcription_request(db: NoSqlDb, user: dict):
    logger.info("===============get_all_transcription_request called==============")
    return db.get_all_items("transcription_request")

# read - get an item
def get_transcription_request(id: str, db: NoSqlDb, user: dict):
    logger.info("===============get_transcription_request called==============")
    logger.info(f"Received request to retrieve transcription_request with id: {id}")
    item = db.get_item("transcription_request", id)
    return item

# write - update an item (without modifying ID)
def update_transcription_request(id: str, new_item: TranscriptionRequest, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============update_transcription_request called==============")
    logger.info(new_item)
    db.update_item("transcription_request", id, new_item.model_dump())
    return db.get_item("transcription_request", id)

# write - delete an item
def delete_transcription_request(id: str, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============delete_transcription_request called==============")
    logger.info(f"Received request to delete transcription_request with id {id}")
    item = db.get_item("transcription_request", id)
    if not item:
        logger.warning(f"TranscriptionRequest with id {id} not found")
        return None
    db.delete_item("transcription_request", id)
    return item