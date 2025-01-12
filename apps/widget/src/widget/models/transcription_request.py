from pydantic import BaseModel
from typing import List, Optional

class Transcription_request(BaseModel):
    id: int
    files: list[str]
