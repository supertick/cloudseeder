from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Transcription(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    type: str
    status: str
    files_path: str
    modified: Optional[int] = Field(None, example=1683123456789)
