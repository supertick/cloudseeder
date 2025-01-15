import logging
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from ai_core.config import settings
from auth.factory import get_auth_provider
import jwt
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"App Setting: {settings}")

app = FastAPI(title="Ai Core", version="0.0.0")

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
from .api.config_api import router as config_router
app.include_router(config_router, prefix='/v1', tags=["Config"])
from .api.company_api import router as company_router
app.include_router(company_router, prefix='/v1', tags=["Company"])
from .api.user_api import router as user_router
app.include_router(user_router, prefix='/v1', tags=["User"])
from .api.role_api import router as role_router
app.include_router(role_router, prefix='/v1', tags=["Role"])
from .api.transcription_request_api import router as transcription_request_router
app.include_router(transcription_request_router, prefix='/v1', tags=["Transcription Request"])
from .api.transcription_api import router as transcription_router
app.include_router(transcription_router, prefix='/v1', tags=["Transcription"])
from .api.transcription_result_api import router as transcription_result_router
app.include_router(transcription_result_router, prefix='/v1', tags=["Transcription Result"])



auth = get_auth_provider()
security = HTTPBearer()

# Fake in-memory user database
fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "secret",
        "role": ["admin", "toolkit"]
    },
    "mary@company1.com": {
        "username": "mary@company1.com",
        "password": "secret",
        "role": ["company1_admin", "company1_user"]
    },
    "bob@company1.com": {
        "username": "bob@company1.com",
        "password": "secret",
        "role": ["company1_user"]
    },
    "anika@company2.com": {
        "username": "anika@company2.com",
        "password": "secret",
        "role": ["company2_admin", "company1_user"]
    },
    "chandra@company2.com": {
        "username": "chandra@company2.com",
        "password": "secret",
        "role": ["company2_user"]
    }

}

# Secret key for signing JWT tokens
SECRET_KEY = "mysecretkey"

# OAuth2 scheme for protecting API routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login route to authenticate users and return a JWT token."""
    logger.info(f"Received login request: {form_data}")

    user = fake_users_db.get(form_data.username)

    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT token
    token = jwt.encode(
        {"sub": user["username"], "role": user["role"], "exp": time.time() + 3600},
        SECRET_KEY,
        algorithm="HS256"
    )
    logger.info(f"Authenticated user: {user} with token: {token}")
    provider_token = auth.authenticate(form_data.username, form_data.password, token)

    return {"access_token": token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn
    print(f"Running on port: {settings.port}")
    uvicorn.run(app, host="0.0.0.0", port=settings.port, reload=True)