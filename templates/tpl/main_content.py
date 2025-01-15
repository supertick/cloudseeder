import logging
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from {app_name}.config import settings
from auth.factory import get_auth_provider
import jwt
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"App Setting: {settings}")

app = FastAPI(title="{AppTitle}", version="0.0.0")

# Allow all CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open to all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# private_router = APIRouter(
#     dependencies=[Depends(require_authentication)]  # Auth required for all private routes
# )

# Include API routes
{API_ROUTES}


auth = get_auth_provider()
security = HTTPBearer()


# Secret key for signing JWT tokens
SECRET_KEY = "mysecretkey"

# OAuth2 scheme for protecting API routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
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