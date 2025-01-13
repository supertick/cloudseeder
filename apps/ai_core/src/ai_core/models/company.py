from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Company(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    name: str
    description: str
    users: list[str]
    modified: int = Field(default_factory=lambda: int(time.time() * 1000), example=1683123456789)
