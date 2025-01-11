from pydantic import BaseModel

class {AppName}(BaseModel):
    name: str
    description: str

# class {AppName}Base(BaseModel):
#     name: str
#     description: str

class {AppName}Response({AppName}):
    id: str  # Include ID in the response
