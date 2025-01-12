from pydantic import BaseModel

class {ModelName}(BaseModel):
    name: str
    description: str

# class {ModelName}Base(BaseModel):
#     name: str
#     description: str

class {ModelName}Response({ModelName}):
    id: str  # Include ID in the response
