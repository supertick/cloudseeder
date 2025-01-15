import logging
import hashlib
import uuid
import json
import os
from typing import Optional
from .interface import AuthProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_DATA_FILE = os.path.join("data","local_auth_store.json")

class LocalAuthProvider(AuthProvider):
    """Local authentication provider (persists user data to a JSON file)."""

    def __init__(self):
        self.users = {}  # In-memory store: {username: {password_hash, token}}
        self._load_users()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _save_users(self):
        """Persist users to a JSON file."""
        if not os.path.exists(os.path.dirname(USER_DATA_FILE)):
            os.makedirs(os.path.dirname(USER_DATA_FILE))
        with open(USER_DATA_FILE, "w") as f:
            json.dump(self.users, f)

    def _load_users(self):
        """Load users from a JSON file if it exists."""
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                try:
                    self.users = json.load(f)
                except json.JSONDecodeError:
                    self.users = {}

    def register_user(self, username: str, password: str) -> dict:
        if username in self.users:
            raise ValueError("User already exists")
        password_hash = self._hash_password(password)
        self.users[username] = {"password_hash": password_hash, "token": None}
        self._save_users()
        return {"username": username, "message": "User registered"}

    def authenticate(self, username: str, password: str, in_token: str = None) -> Optional[str]:
        logger.info(f"authenticate: User {username} password: {password} in_token: {in_token}")
        user = self.users.get(username)
        if user and user["password_hash"] == self._hash_password(password):
            token = str(uuid.uuid4())  # Simple token generation
            logger.info(f"authenticate: User {username} token: {token} in_token: {in_token}")
            if (in_token):
                self.users[username]["token"] = in_token
            else:
                self.users[username]["token"] = token
            self._save_users()
            return token
        return None

    def get_user(self, token: str) -> Optional[dict]:
        for username, data in self.users.items():
            if data.get("token") == token:
                logger.info(f"MATCH !!! get_user: User {username} found")
                return {"username": username}
        return None

    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """Local implementation doesn't use refresh tokens, just return a new token."""
        for username, data in self.users.items():
            if data.get("token") == refresh_token:
                new_token = str(uuid.uuid4())
                self.users[username]["token"] = new_token
                self._save_users()
                return new_token
        return None

    def logout(self, token: str) -> bool:
        for username, data in self.users.items():
            if data.get("token") == token:
                self.users[username]["token"] = None
                self._save_users()
                return True
        return False
