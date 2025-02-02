#!/usr/bin/env python3

import json
import openai
from ai_core.config import settings
from ai_core.models.transcription_request import TranscriptionRequest
from ai_core.services.transcription_request_service import create_transcription_request
from queues.factory import get_queue_client
from ai_core.answer_questions import answer_questions
from datetime import datetime
from ai_core.deepgram_transcription import transcribe, transform

def lambda_handler(event, context):
    # Log the received event
    print("Received event:", json.dumps(event, indent=2))

    # Get the body from the event
    body = event.get("body")
    if body is None:
        raise ValueError("No body found in the event.")

    # If the body is a JSON string, convert it to a dict
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON in event body") from e

    # Convert the dictionary to a TranscriptionRequest instance
    transcription_request = TranscriptionRequest.model_validate(body)

    # Now, you can use transcription_request with your business logic
    # For example, pass it to your create_transcription_request function:
    # create_transcription_request(transcription_request, db, q, user)
    create_transcription_request(transcription_request, None, None, None)

    # Optionally, return a response
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Transcription request processed."})
    }