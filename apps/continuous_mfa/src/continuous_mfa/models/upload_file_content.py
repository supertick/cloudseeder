from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class UploadFileContent(BaseModel):
    id: Optional[str] = Field(None, example="john@company1.com-1683123456789")
    user_id: str = Field(None, example="john@company1.com")
    upload_date: int = Field(None, example=1683123456789)
    filename: str = Field(None, example="file1.txt")
    data: str = Field(None, description="Base64 encoded file data", example="base64 encoded data")
