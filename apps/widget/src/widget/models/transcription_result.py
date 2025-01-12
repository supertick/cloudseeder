from pydantic import BaseModel
from typing import List, Optional

class Transcription_result(BaseModel):
    id: str
    type: str
    status: str
    files: list[str]
