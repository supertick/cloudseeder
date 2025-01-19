from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class User_product_access(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    user_id: str
    product_id: str
    access: bool
    hidden: bool
