from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from widget.api import widget as widget_routes

app = FastAPI()

# Allow all CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open to all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(widget_routes.router, prefix="/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)