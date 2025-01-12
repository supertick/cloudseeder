from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    email: str
    roles: list[str]
