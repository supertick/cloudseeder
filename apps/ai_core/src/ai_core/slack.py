import logging
from ai_core.config import settings
from slack_sdk import WebClient
logger = logging.getLogger(__name__)

slack_client = None

def send_slack_message(message: str):
    """
    Send a message to Slack Channel using Bot User
    """
    global slack_client

    try:
        if slack_client is None and settings.slack_enabled:
            slack_client = WebClient(token=settings.slack_bot_token)

        # if settings.use_slack
        if slack_client:
            slack_client.chat_postMessage(
                channel=settings.slack_channel, 
                text=settings.slack_prefix + message
            )
    except Exception as e:
        raise e
