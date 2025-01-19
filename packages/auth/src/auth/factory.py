import os
from typing import Callable, Dict
from database.factory import get_db
from .cognito import CognitoAuthProvider
from .local_auth import LocalAuthProvider
from .interface import AuthProvider

def get_auth_provider(config_provider: Callable[[], Dict[str, str]]) -> AuthProvider:
    """
    Factory method to return an AuthProvider instance based on the configuration.

    :param config_provider: A callable that returns the configuration dictionary.
    :return: An instance of AuthProvider.
    """
    config = config_provider()  # Get configuration dynamically
    auth_type = config.get("auth_type", "local").lower()  # Default to local auth

    if auth_type == "cognito":
        return CognitoAuthProvider(config=config)
    elif auth_type == "local":
        # Pass `get_db` as the database_factory to `LocalAuthProvider`
        return LocalAuthProvider(config=config, database_factory=get_db)
    else:
        raise ValueError(f"Unsupported auth_type: {auth_type}")