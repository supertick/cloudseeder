# Use an official Python 3.10 image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the ai_core application
COPY apps/ai_core /app/apps/ai_core

# Copy shared packages
COPY packages/auth /app/packages/auth
COPY packages/database /app/packages/database
COPY packages/queues /app/packages/queues

RUN pip install -e apps/ai_core \
    && pip install -e packages/auth \
    && pip install -e packages/database \
    && pip install -e packages/queues

WORKDIR /app/apps/ai_core

# Expose port 8000 for FastAPI
EXPOSE 8000

# Set environment variables (optional fallback values)
# FIXME - dynamically pull config elements from tpl definition
ENV AI_CORE_PORT=8001
ENV AI_CORE_WORK_DIR="/work"
ENV AI_CORE_LOG_LEVEL="info"
ENV AI_CORE_DEEPGRAM_API_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Command to run the FastAPI application
# CMD ["uvicorn", "ai_core.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "src/ai_core/pipeline.py"]
