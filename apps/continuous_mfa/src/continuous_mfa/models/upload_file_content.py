from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Upload_file_content(BaseModel):
    id: Optional[str] = Field(None, example="john@company1.com-1683123456789")
    user_id: str
    upload_date: int
    filename: str
    data: str
