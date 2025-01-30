FROM python:3.10-slim

WORKDIR /app

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

# CWD of the app
WORKDIR /app/apps/ai_core

EXPOSE 8001

CMD ["python", "src/ai_core/pipeline.py"]
