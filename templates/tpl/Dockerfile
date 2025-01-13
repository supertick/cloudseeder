# Use an official Python 3.10 image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app/{app_name}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency files first for efficient caching
COPY apps/{app_name}/pyproject.toml apps/{app_name}/poetry.lock* ./

# Install dependencies using Poetry
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Copy the {app_name} application
COPY apps/{app_name} /app

# Copy shared packages
COPY packages/auth /app/packages/auth
COPY packages/database /app/packages/database
COPY packages/queues /app/packages/queues

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "{app_name}.main:app", "--host", "0.0.0.0", "--port", "8000"]
