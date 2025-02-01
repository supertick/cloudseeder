import logging
from queues.interface import QueueClient
from database.interface import NoSqlDb
from ai_core.models.transcription_result import TranscriptionResult

logger = logging.getLogger(__name__)


def create_transcription_result(item: TranscriptionResult, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============TranscriptionResult service called==============")
    logger.info(item)