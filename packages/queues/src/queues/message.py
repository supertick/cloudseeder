from pydantic import BaseModel, Field
from typing import Any, Optional, Literal
from datetime import datetime
from uuid import UUID, uuid4

class Message(BaseModel):
    name: str = Field(..., description="The name of the message")
    id: UUID = Field(default_factory=uuid4, description="A unique UUID identifier for the message")
    src: str = Field(..., description="Source of the message")
    method: str = Field(..., description="The method related to the message")
    type: Literal["async", "block"] = Field(..., description="Message type: 'async' or 'block'")
    data: Optional[Any] = Field(None, description="Payload that can contain any type or be None")
    ts: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the message in UTC")
