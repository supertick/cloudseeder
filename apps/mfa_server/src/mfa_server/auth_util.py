import logging
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.factory import get_auth_provider


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth = get_auth_provider()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Get current authenticated user from token."""
    logger.info(f"Getting current user from credentials: {credentials}")
    token = credentials.credentials
    logger.info(f"Token: {token}")
    user = auth.get_user(token)
    logger.info(f"User: {user}")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user

def require_role(required_roles: list):
    """Dependency factory for role-based access control."""
    logger.info(f"Creating role checker for required roles: {required_roles}")

    def role_checker(user: dict = Depends(get_current_user)):
        logger.info(f"Checking user roles: {user}")
        user_roles = user.get("role", [])

        # Allow access if no roles are required
        if not required_roles:
            return user

        if "admin" in user_roles:
            return user
                
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Access denied: Insufficient permissions")
        
        return user
    return role_checker
