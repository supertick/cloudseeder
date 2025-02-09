from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import time

class Report(BaseModel):
    id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    product: Optional[str] = Field(None, example="MFALite")
    description: Optional[str] = Field(None, example="Test report")
    user_id: Optional[str] = Field(None, example="john@company1.com")
    input_files: list[str] = Field(default_factory=list, example=["file1.txt", "file2.txt"])
    output_files: list[str] = Field(default_factory=list, example=["file1.txt", "file2.txt"])
    start_datetime: Optional[int] = Field(None, example=1683123456789)
    end_datetime: Optional[int] = Field(None, example=1683123456789)
    status: Optional[str] = None
    exception: Optional[str] = Field(None, example="error")
    modified: Optional[int] = Field(None, example=1683123456789)
