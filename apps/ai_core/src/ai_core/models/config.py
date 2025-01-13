from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Config(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    port: int
    work_dir: str
    log_level: str
    deepgram_api_key: str
    database_type: Literal["tinydb", "dynamodb"] = Field("tinydb", description="Database type", example="dynamodb")
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID", example="your-access-key")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key", example="your-secret-key")
    aws_region: Optional[str] = Field(None, description="AWS Region", example="us-east-1")
    modified: Optional[int] = Field(None, example=1683123456789)
