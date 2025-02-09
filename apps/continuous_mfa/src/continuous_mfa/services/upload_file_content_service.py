import logging
from typing import List
import uuid
import base64
from pathlib import Path
from typing import Dict
from queues.interface import QueueClient
from database.interface import NoSqlDb
from continuous_mfa.models.upload_file_content import UploadFileContent

logger = logging.getLogger(__name__)

# write - Create an item
def create_upload_file_content(item: UploadFileContent, db, q, user: Dict):
    """
    Saves an uploaded file's base64 data to a directory structure:
    data/upload/{user_id}/{upload_date}/{filename}

    Args:
        item (UploadFileContent): The upload file metadata and data.
        db (NoSqlDb): Database client (not used in this function but available for future use).
        q (QueueClient): Queue client (not used in this function but available for future use).
        user (dict): User information (not used, but can be used for additional metadata).

    Returns:
        str: The full path to the saved file.
    """
    logger.info("===============create_upload_file_content called==============")

    # Define the directory structure
    upload_dir = Path(f"data/upload/{item.user_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist

    # Define file path
    file_path = upload_dir / f"{item.upload_date} - {item.filename}"

    try:
        # Decode base64 data and write to file
        with open(file_path, "wb") as file:
            file.write(base64.b64decode(item.data))
        
        logger.info(f"File saved successfully at: {file_path}")

        return {"message": "File uploaded successfully", "file_path": str(file_path)}
    
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return None

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