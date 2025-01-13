import hashlib
import uuid
from typing import Optional
from .interface import AuthProvider

class LocalAuthProvider(AuthProvider):
    """Local authentication provider (fully local storage)."""

    def __init__(self):
        self.users = {}  # Simple in-memory store: {username: {password_hash, token}}

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> dict:
        if username in self.users:
            raise ValueError("User already exists")
        password_hash = self._hash_password(password)
        self.users[username] = {"password_hash": password_hash, "token": None}
        return {"username": username, "message": "User registered"}

    def authenticate(self, username: str, password: str) -> Optional[str]:
        user = self.users.get(username)
        if user and user["password_hash"] == self._hash_password(password):
            token = str(uuid.uuid4())  # Simple token generation
            self.users[username]["token"] = token
            return token
        return None

    def get_user(self, token: str) -> Optional[dict]:
        for username, data in self.users.items():
            if data.get("token") == token:
                return {"username": username}
        return None

    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """Local implementation doesn't use refresh tokens, just return a new token."""
        for username, data in self.users.items():
            if data.get("token") == refresh_token:
                new_token = str(uuid.uuid4())
                self.users[username]["token"] = new_token
                return new_token
        return None

    def logout(self, token: str) -> bool:
        for username, data in self.users.items():
            if data.get("token") == token:
                self.users[username]["token"] = None
                return True
        return False
