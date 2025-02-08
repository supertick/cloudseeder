import json
import logging
import json
import openai
from ai_core.config import settings
from ai_core.config import config_provider
from ai_core.models.transcription_request import TranscriptionRequest
from ai_core.answer_questions import answer_questions
from ai_core.deepgram_transcription import transcribe, transform
from ai_core.services.transcription_request_service import create_transcription_request
from queues.factory import get_queue_client
from datetime import datetime
from database.factory import get_database, get_db
from database.interface import NoSqlDb

# Configure the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_db_provider() -> NoSqlDb:
    return get_database(config_provider)

def process_record(record):
    """
    Process an individual record from the SQS event.
    """
    # Extract the 'body' from the record
    body = record.get("body")
    if body is None:
        raise ValueError(f"No 'body' key found in record: {json.dumps(record)}")
    
    # If the body is a JSON string, parse it into a dict
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON in record body.") from e
    
    # Convert the dict to a TranscriptionRequest instance using Pydantic v2's model_validate
    transcription_request = TranscriptionRequest.model_validate(body)
    
    # Call your business logic with the validated model instance
    # Ensure that create_transcription_request, db, q, and user are defined/imported appropriately
    create_transcription_request(transcription_request, get_db_provider(), None, None)

def lambda_handler(event, context):
    try:
        # Log the entire event for debugging purposes
        logger.info("Received event: %s", json.dumps(event, indent=2))
        
        # Check if the event is from SQS (contains "Records")
        if "Records" in event:
            for record in event["Records"]:
                process_record(record)
        else:
            # If there is no "Records" key, try processing the event as a single record
            process_record(event)
        
        # Return a successful response if everything processed without error
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Transcription request processed."})
        }
    
    except Exception as e:
        # Log the exception along with the full stack trace for debugging
        logger.exception("An error occurred while processing the transcription request.")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }