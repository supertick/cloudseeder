from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Transcription_result(BaseModel):
    id: str
    type: str
    status: str
    files: list[str]
