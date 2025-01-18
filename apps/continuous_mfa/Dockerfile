# Use an official Python 3.10 image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the continuous_mfa application
COPY apps/continuous_mfa /app/apps/continuous_mfa

# Copy shared packages
COPY packages/auth /app/packages/auth
COPY packages/database /app/packages/database
COPY packages/queues /app/packages/queues

RUN pip install -e apps/continuous_mfa \
    && pip install -e packages/auth \
    && pip install -e packages/database \
    && pip install -e packages/queues

# Expose port 8000 for FastAPI
EXPOSE 8000

# Set environment variables (optional fallback values)
# FIXME - dynamically pull config elements from tpl definition
ENV CONTINUOUS_MFA_PORT=8000
ENV CONTINUOUS_MFA_WORK_DIR="/work"
ENV CONTINUOUS_MFA_LOG_LEVEL="info"
ENV CONTINUOUS_MFA_DEEPGRAM_API_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Command to run the FastAPI application
CMD ["uvicorn", "continuous_mfa.main:app", "--host", "0.0.0.0", "--port", "8000"]
