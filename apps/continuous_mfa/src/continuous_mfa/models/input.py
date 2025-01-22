from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Input(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    title: Optional[str] = Field(None, example="Input File 1")
    user_id: Optional[str] = Field(None, example="john@company1.com")
    files: List[str]
    upload_date: Optional[int] = Field(None, example=1683123456789)
