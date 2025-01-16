from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Company(BaseModel):
    id: Optional[str] = Field(None)
    name: str
    description: str
    users: list[str]
