from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class User(BaseModel):
    id: Optional[str] = Field(None, example="john@company1.com")
    email: Optional[str] = Field(None, example="john@company1.com")
    password_hash: Optional[str] = Field(None, example="secret")
    roles: list[str]
    modified: Optional[int] = Field(None, example=1683123456789)
