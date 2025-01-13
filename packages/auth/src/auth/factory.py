import os
from .cognito import CognitoAuthProvider
from .local_auth import LocalAuthProvider
from .interface import AuthProvider

def get_auth_provider() -> AuthProvider:
    auth_type = os.getenv("AUTH_PROVIDER", "local")  # Default to local auth

    if auth_type == "cognito":
        return CognitoAuthProvider(
            user_pool_id=os.getenv("COGNITO_USER_POOL_ID"),
            client_id=os.getenv("COGNITO_CLIENT_ID"),
        )
    else:
        return LocalAuthProvider()
