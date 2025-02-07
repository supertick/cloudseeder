import logging
import json
from fastapi import FastAPI, Request, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from .error_util import log_exception, create_error_response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from continuous_mfa.config import settings
from auth.factory import get_auth_provider
from .config import config_provider
import jwt
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"App Setting: {json.dumps(settings.model_dump(), indent=2)}")

app = FastAPI(title="Continuous Mfa", version="0.0.0")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handles all uncaught exceptions."""
    log_exception(exc)
    # Include the exception's message in the response for debugging
    return create_error_response(
        detail=f"An unexpected error occurred: {str(exc)}",
        status_code=500
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles HTTP exceptions."""
    log_exception(exc)
    return create_error_response(detail=exc.detail, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles validation errors."""
    log_exception(exc)
    return create_error_response(detail="Invalid request data.", status_code=422)


# Allow all CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# private_router = APIRouter(
#     dependencies=[Depends(require_authentication)]  # Auth required for all private routes
# )

# Include API routes
from .api.config_api import router as config_router
app.include_router(config_router, prefix='/v1', tags=["Config"])
from .api.user_api import router as user_router
app.include_router(user_router, prefix='/v1', tags=["User"])
from .api.user_product_access_api import router as user_product_access_router
app.include_router(user_product_access_router, prefix='/v1', tags=["User Product Access"])
from .api.product_api import router as product_router
app.include_router(product_router, prefix='/v1', tags=["Product"])
from .api.input_api import router as input_router
app.include_router(input_router, prefix='/v1', tags=["Input"])
from .api.run_api import router as run_router
app.include_router(run_router, prefix='/v1', tags=["Run"])
from .api.report_api import router as report_router
app.include_router(report_router, prefix='/v1', tags=["Report"])
from .api.upload_file_content_api import router as upload_file_content_router
app.include_router(upload_file_content_router, prefix='/v1', tags=["Upload File Content"])



auth = get_auth_provider(config_provider)
security = HTTPBearer()


# Secret key for signing JWT tokens
SECRET_KEY = "mysecretkey"

# OAuth2 scheme for protecting API routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/v1/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login route to authenticate users and return a JWT token."""
    logger.info(f"Received login request: {form_data}")

    token = auth.authenticate(form_data.username, form_data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn
    print(f"Running on port: {settings.port}")
    uvicorn.run(app, host="0.0.0.0", port=settings.port, reload=True)