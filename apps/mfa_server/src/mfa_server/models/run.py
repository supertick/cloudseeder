from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Run(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    product: str
    start_datetime: str
    status: str
    input_dir: str
    output_dir: str
    modified: Optional[int] = Field(None, example=1683123456789)
