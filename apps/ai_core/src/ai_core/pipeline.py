import logging
import json
import os
import asyncio
import time
from uvicorn import Config, Server
from ai_core.config import settings
from ai_core.models.transcription_request import TranscriptionRequest
from ai_core.main import app
from queues.factory import get_queue_client
from ai_core.answer_questions import answer_questions
from datetime import datetime
from ai_core.deepgram_transcription import transcribe, transform


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
                request = TranscriptionRequest(**message)
                logger.info(f"Request: {request}")

                # FIXME - merge multiple audio files into one
                # should only be 1 file per request
                if len(request.files) != 1:
                    raise ValueError("Invalid number of files in the request.")
                
                audio_filename = request.files[0]

                logger.info("stage 1 deepgram transcription")
                deepgram_json = transcribe(audio_filename)
                if not deepgram_json:
                    raise ValueError("Deepgram transcription failed.")
                
                parent_dir = os.path.join(settings.work_dir, request.patient_id, request.encounter_id)
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

                answers_json = answer_questions(conversation_filename, request.patient_id, request.encounter_id, request.assessment_id, None)
                answers_filename = os.path.join(parent_dir, "answers.json")
                with open(answers_filename, "w") as f:
                    f.write(json.dumps(answers_json))
                    logger.info(f"Answers file saved to {answers_filename}")
                
                if not answers_json:
                    raise ValueError("Answers generation failed.")

                logger.info("stage 3 openai")

            await asyncio.sleep(1)

        except Exception as e:
            logger.error("An error occurred", exc_info=True)
            # Prefent cpu thrashing
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
