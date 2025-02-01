import logging
from queues.interface import QueueClient
from database.interface import NoSqlDb
from ai_core.models.config import Config

logger = logging.getLogger(__name__)


def create_config(item: Config, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============Config service called==============")
    logger.info(item)