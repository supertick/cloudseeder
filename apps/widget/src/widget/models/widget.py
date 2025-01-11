from pydantic import BaseModel

class Widget(BaseModel):
    name: str
    description: str

# class WidgetBase(BaseModel):
#     name: str
#     description: str

class WidgetResponse(Widget):
    id: str  # Include ID in the response
