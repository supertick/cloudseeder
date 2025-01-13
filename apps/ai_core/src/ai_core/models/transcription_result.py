from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Transcription_result(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    type: str
    status: str
    files: list[str]
