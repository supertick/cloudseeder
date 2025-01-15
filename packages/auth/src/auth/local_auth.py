import logging
import hashlib
import json
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from .interface import AuthProvider
from threading import Lock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_DATA_FILE = os.path.join("data", "local_auth_store.json")
JWT_SECRET_KEY = "your_secret_key"  # Replace with a secure key
JWT_EXPIRATION_MINUTES = 60  # Token expiration time


class LocalAuthProvider(AuthProvider):
    """Local authentication provider (persists user data to a JSON file, uses JWT for tokens)."""

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    cls._instance = super(LocalAuthProvider, cls).__new__(cls, *args, **kwargs)
                    cls._instance._initialize()  # Initialize singleton instance
        return cls._instance

    def _initialize(self):
        """Custom initialization for singleton."""
        self.users = {}
        if not os.path.exists(USER_DATA_FILE):
            # Ensure the directory exists
            if not os.path.exists(os.path.dirname(USER_DATA_FILE)):
                os.makedirs(os.path.dirname(USER_DATA_FILE))
            
            # Auto Create the file with an admin user - TODO - should probably generate a random password
            # and save it out to a file locally
            logger.info("USER_DATA_FILE not found. Creating a new one with an admin user.")
            admin_password_hash = self._hash_password("secret")
            self.users["admin"] = {
                "password_hash": admin_password_hash,
                "token": None
            }
            self._save_users()
        else:
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

    def _generate_jwt(self, username: str) -> str:
        """Generate a JWT for the given username."""
        payload = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES),
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
        return token if isinstance(token, str) else token.decode("utf-8")

    def _verify_jwt(self, token: str) -> Optional[dict]:
        """Verify a JWT and return its payload if valid."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT has expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT")
        return None

    def register_user(self, username: str, password: str) -> dict:
        if username in self.users:
            raise ValueError("User already exists")
        password_hash = self._hash_password(password)
        self.users[username] = {"password_hash": password_hash, "token": None}
        self._save_users()
        return {"username": username, "message": "User registered"}

    def authenticate(self, username: str, password: str) -> Optional[str]:
        logger.info(f"Authenticating user: {username}")
        user = self.users.get(username)
        if user and user["password_hash"] == self._hash_password(password):
            token = self._generate_jwt(username)
            self.users[username]["token"] = token
            self._save_users()
            return token
        return None

    def get_user(self, token: str) -> Optional[dict]:
        payload = self._verify_jwt(token)
        if payload:
            username = payload.get("sub")
            stored_token = self.users.get(username, {}).get("token")
            logger.info(f"get_user: stored_token: {stored_token}, provided_token: {token}")
            if username in self.users and stored_token == token:
                return {"username": username}
        return None

    def refresh_token(self, refresh_token: str) -> Optional[str]:
        payload = self._verify_jwt(refresh_token)
        if payload:
            username = payload.get("sub")
            if username in self.users:
                new_token = self._generate_jwt(username)
                self.users[username]["token"] = new_token
                self._save_users()
                return new_token
        return None

    def logout(self, token: str) -> bool:
        payload = self._verify_jwt(token)
        if payload:
            username = payload.get("sub")
            if username in self.users:
                self.users[username]["token"] = None
                self._save_users()
                return True
        return False
