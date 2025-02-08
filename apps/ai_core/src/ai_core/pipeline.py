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
from ai_core.services.transcription_request_service import create_transcription_request
from database.factory import get_database
from database.interface import NoSqlDb

logger = logging.getLogger(__name__)

def get_db_provider() -> NoSqlDb:
    return get_database(config_provider)

def get_queue() -> QueueClient:
    queue_type = settings.queue_type  # Read from app config

    q_params: Dict[str, str] = {}

    if not queue_type:
        return None

    if queue_type == "local":
        q_params = {}
    elif queue_type == "sqs":
        q_params = {
           "queue_url": settings.queue_url
        }

    return get_queue_client(None, queue_type, **q_params)  # Pass to factory


async def start_fastapi():
    """Starts the FastAPI application."""
    logger.info("Starting FastAPI app...")
    logger.info(f"App Setting: {settings}")
    config = Config(app, host="0.0.0.0", port=settings.port, reload=False)
    server = Server(config)
    await server.serve()

async def start_queue_listener(queue_name="ai_core_input", queue_type="sqs"):
    """Starts listening to the queue and processing messages."""
    # Get the queue client instance
    queue_client = get_queue()

    logger.info(f"Listening on queue '{queue_name}' of type '{queue_type}'...")
    while True:
        try:
            # Receive and process messages
            message = queue_client.receive_message()
            if message:
                logger.info(f"Received message: {message}")
                
                # FIXME - There should be a common metadata field for all messages & data field name
                # No Common MetaData or Field Name For Actual Data !
                # AWS SQS sends message in "Body" field
                body = message["Body"]
                recipient_handle = message["ReceiptHandle"]

                request = TranscriptionRequest(**json.loads(body))
                logger.info(f"Transcription Request: {request}")

                logger.info(f"starting transcription {request.id}")
                create_transcription_request(request, get_db_provider(), None, None)
                logger.info(f"procesed transcription {request.id}")
                queue_client.delete_message(recipient_handle)
                logger.info(f"Deleted message with handle {recipient_handle}")

            await asyncio.sleep(1)

        except Exception as e:
            logger.error("An error occurred", exc_info=True)
            # prevent cpu thrashing
            await asyncio.sleep(1)
        


async def main():
    """Starts the FastAPI app and the queue listener concurrently."""
    queue_name = "transcription_request"

    logger.setLevel(settings.log_level)

    await asyncio.gather(
        start_fastapi(),  # Start the FastAPI server
        start_queue_listener(queue_name, settings.queue_type),  # Start the queue listener
    )

if __name__ == "__main__":
    asyncio.run(main())
