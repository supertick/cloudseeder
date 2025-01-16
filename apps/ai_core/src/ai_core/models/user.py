from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class User(BaseModel):
    id: Optional[str] = Field(None, example="admin@scribble.ai")
    full_name: Optional[str] = Field(None, example="John Doe")
    password_hash: Optional[str] = Field(None, example="secret")
    email: str
    roles: list[str]
