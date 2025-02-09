import logging
import requests
import json
from continuous_mfa.config import settings

logger = logging.getLogger(__name__)

def send_google_chat_message(message: str):

    if not settings.google_chat_enabled:
        logger.info("Google Chat messaging disabled")
        return

    message = {
        "text": settings.google_chat_prefix + "\n" + message
    }

    response = requests.post(settings.google_chat_webhook, json=message)

    if response.status_code == 200:
        logger.info("Message sent successfully!")
    else:
        logger.error(f"Failed to send message: {response.text}")

