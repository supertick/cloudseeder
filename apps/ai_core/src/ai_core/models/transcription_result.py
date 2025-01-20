from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Transcription_result(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    type: Literal["deepgram", "aws-transcribe"] = Field("tinydb", description="transcription type", example="deepgram")
    status: str
    created: Optional[int] = Field(None, example=1683123456789)
    patient: str
    encounter: str
    assessment: str
    files: list[str]
