from pydantic import BaseModel
from typing import List, Optional

class Transcription(BaseModel):
    id: int
    type: str
    status: str
    files_path: str
