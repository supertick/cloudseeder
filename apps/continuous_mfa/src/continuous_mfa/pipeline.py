import logging
import git
import traceback
import asyncio
import time
import uvicorn
from uvicorn import Config, Server
from continuous_mfa.generate_ssl import generate_self_signed_cert
from continuous_mfa.config import settings
from continuous_mfa.models.report import Report
from continuous_mfa.main import app  # Import the FastAPI app
from queues.factory import get_queue_client  # Import the queue factory
from continuous_mfa.config import config_provider  # Import the config provider
from datetime import datetime
logger = logging.getLogger(__name__)


async def start_fastapi():
    """Starts FastAPI asynchronously within the event loop."""
    print(f"Running on port: {settings.port}")

    ssl_options = {}
    if settings.ssl_enabled:
        print("SSL enabled")
        generate_self_signed_cert()
        ssl_options = {
            "ssl_keyfile": "key.pem",
            "ssl_certfile": "cert.pem",
        }

    config = Config(app, host="0.0.0.0", port=settings.port, **ssl_options)
    server = Server(config)
    await server.serve() 


async def start_queue_listener():
    """Starts listening to the queue and processing messages."""
    # Get the queue client instance
    queue_client = get_queue_client("input")

    logger.info(f"Listening on queue \"input\" of type '{settings.queue_type}'...")
    while True:
        # Receive and process messages
        message = queue_client.receive_message()
        if message:
            logger.info(f"Received message: {message}")
            # Process the message (e.g., call specific handlers)
            queue_client.delete_message(message["id"])

            report = Report()
            report.start_datetime = datetime.utcnow().timestamp()
            report.user_id = message.get("user_id")
            report.product = message.get("product")
            report.title = message.get("title")
            report.input_files = []
            report.output_files = []
            report.status = "started"

            logger.info(f"Report: {report}")

            # if no user_id process exception

            # check if the user has access to the product
            # if not process exception

            # get_database

        await asyncio.sleep(1)

        # FIXME - verify user_id matches auth of rest api from where
        # user_id = message.get("user_id")



def check_and_pull_updates(interval, config):
    """Checks for updates to the repository and pulls them if available."""
    while True:
        try:
            config = config_provider()
            repo = git.Repo(config.workspace)
            origin = repo.remotes.origin
            origin.fetch()
            local_commit = repo.head.commit
            remote_commit = repo.commit('origin/main')
            if local_commit != remote_commit:
                logger.info("Updates available. Pulling updates...")
                origin.pull()
                logger.info("Updates pulled successfully.")
            else:
                logger.info("No updates available.")
        except git.exc.InvalidGitRepositoryError:
            logger.error("Error: The specified directory is not a valid Git repository.")
        except git.exc.GitCommandError as e:
            logger.error(f"Git command error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e} {traceback.format_exc()}")
        time.sleep(interval)


async def main():
    """Starts the FastAPI app and the queue listener concurrently."""
    await asyncio.gather(
        start_fastapi(),  # ✅ Start FastAPI server asynchronously
        start_queue_listener(),  # ✅ Start queue listener
    )

if __name__ == "__main__":
    asyncio.run(main())  # ✅ This is now safe because FastAPI runs asynchronously