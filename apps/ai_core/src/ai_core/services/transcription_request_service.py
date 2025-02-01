import logging
from queues.interface import QueueClient
from database.interface import NoSqlDb
from ai_core.models.transcription_request import TranscriptionRequest

logger = logging.getLogger(__name__)


def create_transcription_request(item: TranscriptionRequest, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============TranscriptionRequest service called==============")
    logger.info(item)