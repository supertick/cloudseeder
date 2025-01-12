from pydantic import BaseModel
from typing import List, Optional

class Role(BaseModel):
    id: str
    name: str
    description: str
    products: list[str]
