from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Transcription(BaseModel):
    id: str
    type: str
    status: str
    files_path: str
