from pydantic import BaseModel

class WidgetCreate(BaseModel):
    name: str
    description: str

class WidgetRead(BaseModel):
    uuid: str  # Updated from 'id' to 'uuid'
    name: str
    description: str

    class Config:
        from_attributes = True  # Ensures compatibility with attribute-based models
