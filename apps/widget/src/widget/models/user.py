from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: str
    email: str
    roles: list[str]
