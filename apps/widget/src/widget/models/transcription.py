from pydantic import BaseModel
from typing import List, Optional

class Transcription(BaseModel):
    id: str
    type: str
    status: str
    files_path: str
