import logging
from queues.interface import QueueClient
from database.interface import NoSqlDb
from {app_name}.models.{model_name} import {ModelName}

logger = logging.getLogger(__name__)


def create_{model_name}(item: {ModelName}, db: NoSqlDb, q: QueueClient, user: dict):
    logger.info("==============={ModelName} service called==============")
    logger.info(item)