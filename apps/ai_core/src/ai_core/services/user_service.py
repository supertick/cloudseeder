import logging
from queues.interface import QueueClient
from database.interface import NoSqlDb
from ai_core.models.user import User

logger = logging.getLogger(__name__)


def create_user(item: User, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("===============User service called==============")
    logger.info(item)