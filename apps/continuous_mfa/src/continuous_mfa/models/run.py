from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Run(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    product: Optional[str] = None
    title: Optional[str] = Field(None, example="input-1.xlsx")
    user_id: Optional[str] = Field(None, example="john@company1.com")
    input_dir: Optional[str] = Field(None, example="input_dir")
    output_dir: Optional[str] = Field(None, example="output_dir")
