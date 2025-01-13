from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from ai_core.config import settings
from auth.factory import get_auth_provider
import jwt as pyjwt 
import time

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


auth = get_auth_provider()
security = HTTPBearer()

# Authentication dependency
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Get current authenticated user from token."""
    token = credentials.credentials
    user = auth.get_user(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user

# Fake in-memory user database
fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "secret",
        "role": "admin"
    }
}

# Secret key for signing JWT tokens
SECRET_KEY = "mysecretkey"

# OAuth2 scheme for protecting API routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login route to authenticate users and return a JWT token."""
    user = fake_users_db.get(form_data.username)

    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT token
    token = pyjwt.encode(
        {"sub": user["username"], "role": user["role"], "exp": time.time() + 3600},
        SECRET_KEY,
        algorithm="HS256"
    )

    return {"access_token": token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn
    print(f"Running on port: {settings.port}")
    uvicorn.run(app, host="0.0.0.0", port=settings.port, reload=True)