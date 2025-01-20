from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Transcription_request(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    user_id: str = Field(None, example="john@company1.com")
    prefix: str = Field("work-dir", example="work-dir")
    type: Literal["deepgram", "aws-transcribe"] = Field("tinydb", description="transcription type", example="deepgram")
    files: list[str]
