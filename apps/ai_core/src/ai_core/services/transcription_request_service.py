import logging
import json
import os
import asyncio
import time
from typing import List
import uuid
from queues.interface import QueueClient
from database.interface import NoSqlDb
from uvicorn import Config, Server
from ai_core.config import settings
from ai_core.models.transcription_request import TranscriptionRequest
from ai_core.main import app
from queues.factory import get_queue_client
from ai_core.answer_questions import answer_questions
from datetime import datetime
from ai_core.deepgram_transcription import transcribe, transform


logger = logging.getLogger(__name__)

# write - Create an item
def create_transcription_request(item: TranscriptionRequest, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_transcription_request called==============")
    logger.info("*********************************************************")
    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - merge multiple audio files into one
    # should only be 1 file per request
    if len(item.files) != 1:
        raise ValueError("Invalid number of files in the request.")
    
    audio_filename = item.files[0]

    logger.info("stage 1 deepgram transcription")
    deepgram_json = transcribe(audio_filename)
    if not deepgram_json:
        raise ValueError("Deepgram transcription failed.")
    
    parent_dir = os.path.join(settings.work_dir, item.patient_id, item.encounter_id)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    # publish timings metrics errors slack ?
    # save or push file to storage for debugging
    output_file = os.path.join(parent_dir, "deepgram.json")
    with open(output_file, "w") as f:
        f.write(deepgram_json)

    logger.info("stage 2 deepgram transformation")
    conversation_json = transform(deepgram_json)
    if not conversation_json:
        raise ValueError("Conversation transformation failed.")
    
    conversation_filename = os.path.join(parent_dir, "conversation.json")
    with open(conversation_filename, "w") as f:
        f.write(json.dumps(conversation_json))
        logger.info(f"Conversation file saved to {conversation_filename}")

    answers_json = answer_questions(conversation_filename, item.patient_id, item.encounter_id, item.assessment_id, None)
    answers_filename = os.path.join(parent_dir, "answers.json")
    with open(answers_filename, "w") as f:
        f.write(json.dumps(answers_json))
        logger.info(f"Answers file saved to {answers_filename}")
    
    if not answers_json:
        raise ValueError("Answers generation failed.")

    logger.info("stage 3 openai")

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