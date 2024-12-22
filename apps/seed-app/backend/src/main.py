from fastapi import FastAPI
from src.api.widgets import router as widget_router

app = FastAPI(  # pylint: disable=invalid-name
    title="CloudSeeder",
    description="Seed App API",
    version="0.1.0",
)

# Add routes
app.include_router(widget_router, prefix="/widgets", tags=["Widgets"])
