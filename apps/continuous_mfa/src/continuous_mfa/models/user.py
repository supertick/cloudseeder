from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class User(BaseModel):
    id: Optional[str] = Field(None, example="john@company1.com")
    fullname: Optional[str] = Field(None, example="John Doe")
    email: Optional[str] = Field(None, example="john@company1.com")
    password_hash: Optional[str] = Field(None, example="secret")
    roles: Optional[list[str]] = Field(None, example=["admin"])
    login_count: Optional[int] = Field(None, example=5)
    last_login: Optional[int] = Field(None, example=1683123456789)
    last_unsuccessful_login: Optional[int] = Field(None, example=1683123456789)
