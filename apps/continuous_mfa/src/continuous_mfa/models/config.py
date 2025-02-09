from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Config(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    ssl_enabled: Optional[bool] = Field(False, description="Enable SSL", example=True)
    auth_enabled: Optional[bool] = Field(False, description="Enable authentication", example=True)
    database_type: Literal["tinydb", "dynamodb"] = Field("tinydb", description="Database type", example="dynamodb")
    debug: Optional[bool] = Field(True, description="Enable debug mode", example=True)
    queue_type: Literal["local", "noop", "sqs", "azure"] = Field("local", description="Database type", example="local")
    port: Optional[int] = Field(8000, example=8000)
    log_level: Optional[str] = Field("INFO", example="INFO")
    work_dir: Optional[str] = Field("work", example="work")
    aws_access_key_id: Optional[str] = Field(None, description="AWS Access Key ID", example="your-access-key")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS Secret Access Key", example="your-secret-key")
    aws_region: Optional[str] = Field(None, description="AWS Region", example="us-east-1")
    mfatwin_dir: Optional[str] = Field("mfatwin", example="mfatwin")
    google_chat_enabled: Optional[bool] = Field(True, description="Enable Google Chat Messaging", example=True)
    google_chat_webhook: Optional[str] = Field("https://chat.googleapis.com/v1/spaces/AAAA40PP240/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=NfZbb_efOlZ7dF8jLET9XoEkTA6mEf7GXMtCG4RZEG8", example="https://chat.googleapis.com/v1/spaces/AAAA40PP240/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=NfZbb_efOlZ7dF8jLET9XoEkTA6mEf7GXMtCG4RZEG8")
    google_chat_prefix: Optional[str] = Field("🚀 *Dev Continuous MFA*\n Testing Continuous MFA Messaging [GitHub continuous_mfa](https://github.com/Metalyticsbio/continuous_mfa)", example="Continuous MFA")
    version: Optional[str] = Field("0.0.0", example="0.1.0")
