from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Config(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    auth_enabled: Optional[bool] = Field(False, description="Enable authentication", example=True)
    database_type: Literal["tinydb", "dynamodb"] = Field("tinydb", description="Database type", example="dynamodb")
    debug: Optional[bool] = Field(True, description="Enable debug mode", example=True)
    queue_type: Literal["local", "sqs"] = Field("local", description="Database type", example="local")
    port: Optional[int] = Field(None, example=8000)
    log_level: Optional[str] = Field(None, example="info")
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID", example="your-access-key")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key", example="your-secret-key")
    aws_region: Optional[str] = Field(None, description="AWS Region", example="us-east-1")
