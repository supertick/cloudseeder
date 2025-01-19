from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class User_product_access(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    user_id: Optional[str] = Field(None, example="john@company1.com")
    product_id: Optional[str] = Field(None, example="CloneSelectMFA")
    access: Optional[bool] = Field(False, example=False)
    enabled: Optional[bool] = Field(False, example=False)
    success: Optional[int] = Field(0, example=0)
    errors: Optional[int] = Field(0, example=0)
