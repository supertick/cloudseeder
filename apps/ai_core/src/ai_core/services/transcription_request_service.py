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
from ai_core.models.transcription_result import TranscriptionResult
from ai_core.main import app
from queues.factory import get_queue_client
from ai_core.answer_questions import answer_questions
from datetime import datetime
from ai_core.deepgram_transcription import transcribe, transform, transcribe_buffer


logger = logging.getLogger(__name__)

# write - Create an item
def create_transcription_request(item: TranscriptionRequest, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============create_transcription_request called==============")
    logger.info(f"settings: [{settings}]")

    result = TranscriptionResult(
                            id=item.id,
                            user_id=item.user_id,
                            patient_id=item.patient_id,
                            assessment_id=item.assessment_id,
                            company_id=item.company_id,
                            transcribe_type=item.transcribe_type,
                            status="processing",
                            started=int(time.time()),
                            answer_files=[]
                        )

    if not db:
        raise ValueError("No database connection provided.")
    
    item_id = item.id if hasattr(item, "id") and item.id else str(uuid.uuid4())
    logger.info(f"Using item_id: {item_id}")
    new_item = item.model_dump()
    new_item["id"] = item_id  # Store UUID in the database

    logger.info(item)

    # FIXME - merge multiple audio files into one
    # should only be 1 file per request
    if len(item.audio_files) != 1:
        raise ValueError("Invalid number of files in the request.")
    
    audio_filename = item.audio_files[0]

    logger.info(f"audio_filename: {audio_filename}")
    prefix = f"{item.user_id}/{item.patient_id}/{item.assessment_id}"

    # db.get_item("input", f"{item.user_id}/{item.patient_id}/{item.assessment_id}/deepgram.json")
    audio_buffer = db.get_binary_item("input", f"{prefix}/{audio_filename}")
    if not audio_buffer:
        raise ValueError(f"Audio file not found in: input/{prefix}/{audio_filename}")

    logger.info("starting deepgram transcription")
    deepgram_json = transcribe_buffer(audio_buffer)
    if not deepgram_json:
        raise ValueError("Deepgram transcription failed for file: input/{prefix}/{audio_filename}")
    
    deepgram_dict = json.loads(deepgram_json)
    
    logger.info(f"saving deepgram transformation {prefix}/deepgram.json")    
    db.insert_item("output", f"{prefix}/deepgram.json", deepgram_dict)
    result.answer_files.append(f"{prefix}/deepgram.json")
    # publish timings metrics errors slack ?
    # save or push file to storage for debugging

    logger.info("deepgram transformation")
    conversation_json = transform(deepgram_json)
    if not conversation_json:
        raise ValueError(f"conversation transformation failed for {deepgram_json}")
    db.insert_item("output", f"{prefix}/conversation.json", conversation_json)
    result.answer_files.append(f"{prefix}/conversation.json")

    logger.info("answer questions")
    answers_json = answer_questions(conversation_json, item.patient_id, item.assessment_id, item.assessment_id)
    
    if not answers_json:
        raise ValueError("Answers generation failed.")

    db.insert_item("output", f"{prefix}/answers.json", answers_json)
    result.answer_files.append(f"{prefix}/answers.json")
    
    logger.info("ai core processing finished")
    return result

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