import logging
from queues.interface import QueueClient
from database.interface import NoSqlDb
from ai_core.models.transcription_request import Transcription_request

logger = logging.getLogger(__name__)


def create_transcription_request(item: Transcription_request, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============Transcription_request service called==============")
    logger.info(item)