from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Config(BaseModel):
    id: Optional[str] = Field("default", example="default")
    port: Optional[int] = Field(8001, example="8001")
    work_dir: Optional[str] = Field("work", example="work")
    log_level: Optional[str] = Field("info", example="info")
    auth_enabled: Optional[bool] = Field(False, description="Enable authentication", example=True)
    database_type: Literal["tinydb", "dynamodb"] = Field("tinydb", description="Database type", example="dynamodb")
    debug: Optional[bool] = Field(True, description="Enable debug mode", example=True)
    queue_type: Literal["local", "sqs"] = Field("local", description="Queue type", example="local")
    deepgram_api_key: Optional[str] = Field(None, example="xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    openai_key: Optional[str] = Field(None, description="OpenAI access key", example="your-access-key")
    openai_model: Optional[str] = Field("gpt-4o-mini", description="OpenAI model", example="gpt-4o-mini")
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID", example="your-access-key")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key", example="your-secret-key")
    aws_region: Optional[str] = Field(None, description="AWS Region", example="us-east-1")
