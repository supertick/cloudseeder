from pydantic import BaseModel
from typing import List, Optional

class Transcription_request(BaseModel):
    id: str
    files: list[str]
