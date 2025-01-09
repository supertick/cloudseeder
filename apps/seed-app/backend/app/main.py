from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.api.widgets import router as widget_router
from pathlib import Path
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def lifespan(app: FastAPI):
    """Lifespan handler for startup and shutdown."""
    # Startup logic
    log.info("Starting up FastAPI application")
    try:
        next_dir = "app/out/_next"
        static_dir = "app/out/_next/static"

        if os.path.isdir(next_dir):
            app.mount("/_next", StaticFiles(directory=next_dir), name="next_static")
            log.info("Mounted /_next static files.")
        else:
            log.warning(f"Directory not found: {next_dir}. Skipping /_next static files.")

        if os.path.isdir(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static_files")
            log.info("Mounted /static static files.")
        else:
            log.warning(f"Directory not found: {static_dir}. Skipping /static static files.")

    except ImportError as e:
        log.error(f"Failed to import OpenSearch verification function: {str(e)}")
    except Exception as e:
        log.error(f"Error during startup: {str(e)}")

    yield  # Control is passed to the app here

    # Shutdown logic (if needed)
    log.info("Shutting down FastAPI application")


app = FastAPI(  # pylint: disable=invalid-name
    title="CloudSeeder",
    description="Seed App API",
    version="0.1.0",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add routes
app.include_router(widget_router, prefix="/widgets", tags=["Widgets"])
