from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Product(BaseModel):
    id: Optional[str] = Field(None, example="BMSMFALite")
    title: Optional[str] = Field(None, example="BMS MFALite")
    description: Optional[str] = Field(None, example="BMS MFALite")
