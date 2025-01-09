from typing import Optional
from pydantic import BaseModel
class Widget(BaseModel):
    uuid: Optional[str] = None
    name: str
    description: Optional[str] = None
