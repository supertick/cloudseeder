from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Company(BaseModel):
    id: str
    name: str
    description: str
    users: list[str]
