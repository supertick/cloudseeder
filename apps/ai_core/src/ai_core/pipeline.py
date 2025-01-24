import logging
import git
import asyncio
import time
from uvicorn import Config, Server
from ai_core.config import settings
from ai_core.models.transcription_request import Transcription_request
from ai_core.main import app  # Import the FastAPI app
from queues.factory import get_queue_client  # Import the queue factory
from ai_core.config import config_provider  # Import the config provider
from datetime import datetime
from ai_core.deepgram_transcription import transcribe
logger = logging.getLogger(__name__)


async def start_fastapi():
    """Starts the FastAPI application."""
    logger.info("Starting FastAPI app...")
    logger.info(f"App Setting: {settings}")
    config = Config(app, host="0.0.0.0", port=settings.port, reload=False)
    server = Server(config)
    await server.serve()

async def start_queue_listener(queue_name, queue_type="local"):
    """Starts listening to the queue and processing messages."""
    # Get the queue client instance
    queue_client = get_queue_client(queue_name, queue_type=queue_type)

    logger.info(f"Listening on queue '{queue_name}' of type '{queue_type}'...")
    while True:
        try:
            # Receive and process messages
            message = queue_client.receive_message()
            if message:
                logger.info(f"Received message: {message}")
                # Process the message (e.g., call specific handlers)            
                queue_client.delete_message(message["id"])
                request = Transcription_request(**message)
                logger.info(f"Request: {request}")

                # FIXME - merge multiple audio files into one

                logger.info(f"Transcribing request: {request}")
                conversation_json_file = transcribe(request)

            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error: {e}")

        # FIXME - verify user_id matches auth of rest api from where
        # user_id = message.get("user_id")

async def main():
    """Starts the FastAPI app and the queue listener concurrently."""
    queue_name = "transcription_request"
    queue_type = "local"  # Replace with "sqs", "azure", etc., as needed

    await asyncio.gather(
        start_fastapi(),  # Start the FastAPI server
        start_queue_listener(queue_name, queue_type),  # Start the queue listener
    )

if __name__ == "__main__":
    asyncio.run(main())
