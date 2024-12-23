from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4

from src.database import get_database
from src.models.widget import Widget

router = APIRouter()

# Dependency to get the database instance
db = get_database()

@router.post("/", response_model=Widget)
def create_widget(widget: Widget):
    """
    Create a new widget with a unique UUID.
    """
    widget_uuid = str(uuid4())
    item = {
        "uuid": widget_uuid,
        "name": widget.name,
        "description": widget.description,
    }
    db.insert_item(item)
    return item

@router.get("/", response_model=List[Widget])
def read_widgets():
    """
    Retrieve all widgets from the database.
    """
    return db.table.all()

@router.get("/{uuid}", response_model=Widget)
def read_widget(uuid: str):
    """
    Retrieve a single widget by UUID.
    """
    widget = db.get_item(uuid)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget

@router.delete("/{uuid}", response_model=dict)
def delete_widget(uuid: str):
    """
    Delete a widget by UUID.
    """
    widget = db.get_item(uuid)
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    db.delete_item(uuid)
    return {"message": f"Widget with UUID {uuid} has been deleted"}
