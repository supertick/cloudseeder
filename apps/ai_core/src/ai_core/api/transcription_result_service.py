import logging
from queues.interface import QueueClient
from database.interface import NoSqlDb
from ai_core.models.transcription_result import Transcription_result

logger = logging.getLogger(__name__)


def create_transcription_result(item: Transcription_result, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============Transcription_result service called==============")
    logger.info(item)