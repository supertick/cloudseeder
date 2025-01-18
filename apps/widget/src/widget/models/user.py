from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class User(BaseModel):
    id: str
    email: str
    roles: list[str]
