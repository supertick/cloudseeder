from pydantic import BaseModel
from typing import List, Optional

class Transcription_result(BaseModel):
    id: int
    type: str
    status: str
    files: list[str]
