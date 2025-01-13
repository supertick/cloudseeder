from pydantic import BaseModel
from typing import List, Optional

class Company(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    users: list[str]
