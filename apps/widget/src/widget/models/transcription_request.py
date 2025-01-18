from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Transcription_request(BaseModel):
    id: str
    files: list[str]
