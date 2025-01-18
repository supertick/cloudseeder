from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Run_status(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    product: str
    start_datetime: str
    end_datetime: str
    status: str
    input_files: list[str]
    output_files: list[str]
    modified: Optional[int] = Field(None, example=1683123456789)
