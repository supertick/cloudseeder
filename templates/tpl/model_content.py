# FIXME - make this an active template
from pydantic import BaseModel, Field
from typing import Optional

class {ModelName}(BaseModel):
    name: str
    description: str

# class {ModelName}Base(BaseModel):
#     name: str
#     description: str

class {ModelName}Response({ModelName}):
    id: str  # Include ID in the response
