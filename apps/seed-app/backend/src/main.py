from fastapi import FastAPI
from src.api.widgets import router as widget_router

app = FastAPI()

# Add routes
app.include_router(widget_router, prefix="/widgets", tags=["Widgets"])
