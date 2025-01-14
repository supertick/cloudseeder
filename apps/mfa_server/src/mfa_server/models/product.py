from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Product(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    name: str
    description: str
    type: str = Field(None, example="string")
    modified: Optional[int] = Field(None, example=1683123456789)
