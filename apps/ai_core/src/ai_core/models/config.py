from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Config(BaseModel):
    id: Optional[str] = Field("default", example="default")
    port: Optional[int] = Field(8001, example="8001")
    work_dir: Optional[str] = Field("work", example="work")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO", description="Log Level", example="INFO")
    auth_enabled: Optional[bool] = Field(False, description="Enable authentication", example=True)
    database_type: Literal["s3", "none", "tinydb", "dynamodb", "filesystem"] = Field("s3", description="Database type", example="dynamodb")
    bucket_name: Optional[str] = Field("scribble2-data", description="S3 bucket name", example="scribble2-data")
    debug: Optional[bool] = Field(True, description="Enable debug mode", example=True)
    queue_only: Optional[bool] = Field(True, description="Run only queue listener - else run FastAPI and queue listener", example=True)
    queue_type: Literal["local", "sqs"] = Field("sqs", description="Queue type", example="local")
    queue_input_name: Optional[str] = Field(None, description="SQS Queue URL", example="https://sqs.us-west-2.amazonaws.com/123456789012/input-queue")
    queue_output_name: Optional[str] = Field(None, description="SQS Queue URL", example="https://sqs.us-west-2.amazonaws.com/123456789012/outpu-queue")
    deepgram_api_key: Optional[str] = Field(None, example="xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    openai_key: Optional[str] = Field(None, description="OpenAI access key", example="your-access-key")
    openai_model: Optional[str] = Field("gpt-4o-mini", description="OpenAI model", example="gpt-4o-mini")
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID", example="your-access-key")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key", example="your-secret-key")
    slack_enabled: Optional[bool] = Field(True, description="Enable Slack notifications", example=True)
    slack_channel: Optional[str] = Field("acutedge-alerts", description="Slack channel", example="acutedge-alerts")
    slack_bot_token: Optional[str] = Field(None, description="Slack bot token", example="xxxxxxxx")
    slack_prefix: Optional[str] = Field(None, description="Prefix to message", example="AI Core - DEV:")
