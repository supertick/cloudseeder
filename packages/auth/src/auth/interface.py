from abc import ABC, abstractmethod
from typing import Optional

class AuthProvider(ABC):
    """Abstract interface for authentication providers."""

    @abstractmethod
    def register_user(self, username: str, password: str) -> dict:
        """Register a new user."""
        pass

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user and return a token if successful."""
        pass

    @abstractmethod
    def get_user(self, token: str) -> Optional[dict]:
        """Retrieve user details from token."""
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """Refresh an authentication token."""
        pass

    @abstractmethod
    def logout(self, token: str) -> bool:
        """Logout the user (invalidate token)."""
        pass
