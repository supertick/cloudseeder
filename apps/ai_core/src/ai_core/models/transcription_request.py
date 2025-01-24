from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Transcription_request(BaseModel):
    id: Optional[str] = None
    user_id: str = Field(None, example="john@companya.com")
    patient_id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    encounter_id: Optional[str] = Field(None, example="0kGa50000000d9REAQ")
    assessment_id: Optional[str] = Field(None, example="001a500000ou2FIAAY")
    company_id: Optional[str] = Field(None, example="CompanyA")
    transcribe_type: Literal["deepgram", "aws-transcribe", "whisper"] = Field("deepgram", description="transcription type", example="deepgram")
    files: list[str] = Field(None, example=["audio_1720195869941.webm", "audio_1720195889351.webm", "audio_1720195889391.webm"])
