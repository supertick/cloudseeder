from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class TranscriptionRequest(BaseModel):
    id: Optional[str] = Field(None, description="Transcription Request ID - can be created by client or will be self generated", example="123e4567-e89b-12d3-a456-426614174000")
    user_id: str = Field(None, description="clinician/user id", example="john@companya.com")
    patient_id: Optional[str] = Field(None, description="patient id - uuid ?", example="001a500000ou2FIAAY")
    assessment_id: Optional[str] = Field(None, description="assessment id - uuid ?", example="001a500000ou2FIAAY")
    company_id: Optional[str] = Field(None, example="CompanyA")
    transcribe_type: Literal["deepgram", "aws-transcribe", "whisper"] = Field("deepgram", description="transcription type", example="deepgram")
    audio_files: list[str] = Field(None, example=["audio_1720195869941.webm"])
    question_files: list[str] = Field(None, ddescription="questions for this assesment", example=["questions.json"])
