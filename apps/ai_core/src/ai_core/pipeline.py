import logging
import json
import os
import asyncio
import time
from datetime import datetime
from typing import Dict
from uvicorn import Config, Server
from ai_core.config import settings
from ai_core.main import app
from queues.factory import get_queue_client
from queues.interface import QueueClient
from queues.factory import get_queue_client
from ai_core.config import settings, config_provider
from ai_core.models.transcription_request import TranscriptionRequest
from ai_core.models.transcription_result import TranscriptionResult
from ai_core.services.transcription_request_service import create_transcription_request
from database.factory import get_database
from database.interface import NoSqlDb

logger = logging.getLogger(__name__)

def get_db_provider() -> NoSqlDb:
    return get_database(config_provider)

# Has flexibility of abstraction - should not be here
# The important part to update and keep is the abstraction between queue types and
# common meta data
def get_input_queue() -> QueueClient:
    queue_type = settings.queue_type  # Read from app config

    q_params: Dict[str, str] = {}

    if not queue_type:
        return None

    if queue_type == "local":
        q_params = {}
    elif queue_type == "sqs":
        q_params = {
           "queue_url": settings.queue_input_url
        }

    return get_queue_client(settings.queue_input_url, queue_type, **q_params)  # Pass to factory

def get_output_queue() -> QueueClient:
    queue_type = settings.queue_type  # Read from app config

    q_params: Dict[str, str] = {}

    if not queue_type:
        return None

    if queue_type == "local":
        q_params = {}
    elif queue_type == "sqs":
        q_params = {
           "queue_url": settings.queue_output_url
        }

    return get_queue_client(settings.queue_output_url, queue_type, **q_params)  # Pass to factory


async def start_fastapi():
    """Starts the FastAPI application."""
    logger.info("Starting FastAPI app...")
    logger.info(f"App Setting: {settings}")
    config = Config(app, host="0.0.0.0", port=settings.port, reload=False)
    server = Server(config)
    await server.serve()

async def start_queue_listener():
    """Starts listening to the queue and processing messages."""
    # Get the queue client instance
    queue_input_client = get_input_queue()
    queue_output_client = get_output_queue()

    logger.info(f"Listening on queue '{settings.queue_input_url}' of type '{settings.queue_type}'...")
    while True:
        try:
            # Receive and process messages
            message = queue_input_client.receive_message()
            if message:
                logger.info(f"received message: {message}")
                
                # FIXME - There should be a common metadata field for all messages & data field name
                # No Common MetaData or Field Name For Actual Data !
                # AWS SQS sends message in "Body" field
                body = message["Body"]
                recipient_handle = message["ReceiptHandle"]

                request = TranscriptionRequest(**json.loads(body))
                logger.info(f"transcription request: {request}")
                
                logger.info(f"starting transcription {request.id}")                
                result = create_transcription_request(request, get_db_provider(), None, None)
                logger.info(f"procesed transcription {request.id}")

                queue_input_client.delete_message(recipient_handle)
                result.completed = int(time.time())
                result.status = "completed"
                message_body = result.model_dump_json()  # Converts Pydantic model to a JSON string
                logger.info(f"sending message to output queue: {message_body}")
                queue_output_client.send_message(message_body)
                logger.info(f"deleted message with handle {recipient_handle}")

            await asyncio.sleep(1)

        except Exception as e:
            logger.error("An error occurred", exc_info=True)
            # prevent cpu thrashing
            await asyncio.sleep(1)
        


async def main():
    """Starts the FastAPI app and the queue listener concurrently."""
    logger.setLevel(settings.log_level)
    if settings.queue_only:
        await asyncio.gather(         
            start_queue_listener(),
        )
    else:
        await asyncio.gather(
            start_fastapi(),
            start_queue_listener()
        )

if __name__ == "__main__":
    asyncio.run(main())
