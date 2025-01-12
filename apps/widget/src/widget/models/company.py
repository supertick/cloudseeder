from pydantic import BaseModel
from typing import List, Optional

class Company(BaseModel):
    id: int
    name: str
    description: str
    users: list[str]
