from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Upload_file_content(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    filename: str
    data: str
