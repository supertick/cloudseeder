from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_core.config import settings

print(f"App Setting: {settings}")

app = FastAPI(title="{AppTitle}", version="0.0.0")

# Allow all CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open to all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
{API_ROUTES}

if __name__ == "__main__":
    import uvicorn
    print(f"Running on port: {settings.port}")
    uvicorn.run(app, host="0.0.0.0", port=settings.port, reload=True)