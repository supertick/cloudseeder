import logging
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from ai_core.models.transcription_result import TranscriptionResult

logger = logging.getLogger(__name__)

# write - Create an item
def create_transcription_result(item: TranscriptionResult, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_transcription_result called==============")

    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - if db: ...
    db.insert_item("transcription_result", item_id, new_item)
    logger.info(f"TranscriptionResult created: {new_item}")
    if q:
        q.send_message(new_item)
        logger.info(f"Message sent to queue: TranscriptionResult created: {new_item}")
        logger.info(f"Queue message count: {q.get_message_count()}")
    return new_item

# read - get all items
def get_all_transcription_result(db: NoSqlDb, user: dict):
    logger.info("===============get_all_transcription_result called==============")
    return db.get_all_items("transcription_result")

# read - get an item
def get_transcription_result(id: str, db: NoSqlDb, user: dict):
    logger.info("===============get_transcription_result called==============")
    logger.info(f"Received request to retrieve transcription_result with id: {id}")
    item = db.get_item("transcription_result", id)
    return item

# write - update an item (without modifying ID)
def update_transcription_result(id: str, new_item: TranscriptionResult, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============update_transcription_result called==============")
    logger.info(new_item)
    db.update_item("transcription_result", id, new_item.model_dump())
    return db.get_item("transcription_result", id)

# write - delete an item
def delete_transcription_result(id: str, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============delete_transcription_result called==============")
    logger.info(f"Received request to delete transcription_result with id {id}")
    item = db.get_item("transcription_result", id)
    if not item:
        logger.warning(f"TranscriptionResult with id {id} not found")
        return None
    db.delete_item("transcription_result", id)
    return item