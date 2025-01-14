from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Company(BaseModel):
    id: Optional[str] = Field(None)
    name: str
    description: str
    users: list[str]
    modified: int = Field(default_factory=lambda: int(time.time() * 1000), example=1683123456789)
