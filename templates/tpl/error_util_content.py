import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from {app_name}.config import settings 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_exception(exc: Exception):
    """Logs the exception details."""
    logger.error(f"An error occurred: {exc}", exc_info=True)

def create_error_response(detail: str, status_code: int = 500):
    """Creates a standardized JSON error response."""
    message = detail if settings.debug else "An unexpected error occurred."
    return JSONResponse(
        status_code=status_code,
        content={"message": message},
    )