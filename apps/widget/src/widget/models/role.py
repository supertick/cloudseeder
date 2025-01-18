from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Role(BaseModel):
    id: str
    name: str
    description: str
    products: list[str]
