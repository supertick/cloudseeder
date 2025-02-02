import logging
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional
from threading import Lock
from .interface import AuthProvider
from database.interface import NoSqlDb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JWT_SECRET_KEY = "your_secret_key"  # Replace with a secure key
JWT_EXPIRATION_MINUTES = 60  # Token expiration time
USERS_TABLE = "user"


from typing import Dict, Callable
from threading import Lock
from database.interface import NoSqlDb
class LocalAuthProvider(AuthProvider):
    """Local authentication provider (uses NoSqlDb for persistence, JWT for tokens)."""

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    # Call the parent __new__ method without passing args/kwargs
                    cls._instance = super(LocalAuthProvider, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: Dict[str, str], database_factory: Callable[[Callable[[], Dict[str, str]]], NoSqlDb]):
        """
        Initialize the local authentication provider.

        :param config: The configuration dictionary.
        :param database_factory: A callable that provides a NoSqlDb instance.
        """
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        # Use the database factory to get a NoSqlDb instance
        self.database = database_factory(lambda: config)

        # Initialize users in the database
        self._initialize_users()

    # WARNING - to have a form of authentication we need a concept of users and roles for authorization
    def _initialize_users(self):
        if not self.database:
            logger.warning("no users cannot do authentication")
            return
        """Ensure the users table exists and create a default admin user if empty."""
        if not self.database.get_all_items(USERS_TABLE):
            logger.info("Initializing default admin user.")
            admin_password_hash = self._hash_password("borkborkbork123")
            self.database.insert_item(
                USERS_TABLE,
                "admin@generator.ai",
                {
                    "id": "admin@generator.ai",
                    "email": "admin@generator.ai",
                    "password_hash": admin_password_hash,
                    "roles": ["admin"],
                    "modified": int(datetime.utcnow().timestamp() * 1000),
                },
            )

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _generate_jwt(self, username: str) -> str:
        """Generate a JWT for the given username."""
        user = self.database.get_item(USERS_TABLE, username)
        if user:
            user.pop("password_hash", None)
            user.pop("password", None)        
            user.pop("token", None)        

        payload = {
            "sub": username,
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES),
            "user": user
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
        if self.database.get_item(USERS_TABLE, username):
            raise ValueError("User already exists")
        password_hash = self._hash_password(password)
        self.database.insert_item(
            USERS_TABLE,
            username,
            {
                "id": username,
                "email": username,
                "password_hash": password_hash,
                "roles": [],
                "modified": int(datetime.utcnow().timestamp() * 1000),
            },
        )
        return {"username": username, "message": "User registered"}

    def authenticate(self, username: str, password: str) -> Optional[str]:
        logger.info(f"Authenticating user: {username}")
        user = self.database.get_item(USERS_TABLE, username)
        if user:
            user["login_count"] = user.get("login_count", 0) + 1
            self.database.update_item(USERS_TABLE, username, user)
            if user["password_hash"] == self._hash_password(password):
                token = self._generate_jwt(username)
                user["token"] = token
                user["last_login"] = int(datetime.utcnow().timestamp() * 1000)
                self.database.update_item(USERS_TABLE, username, user)
                return token
            else:
                self.database.update_item(USERS_TABLE, username, {"last_unsuccessful_login": int(datetime.utcnow().timestamp() * 1000)})
        return None

    def get_user(self, token: str) -> Optional[dict]:
        payload = self._verify_jwt(token)
        if payload:
            username = payload.get("sub")
            user = self.database.get_item(USERS_TABLE, username)
            if user and user.get("token") == token:
                return {"id": user["id"], "email": user["email"], "roles": user.get("roles", [])}
        return None

    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """Generate a new token if the refresh token is valid."""
        payload = self._verify_jwt(refresh_token)
        if payload:
            username = payload.get("sub")
            user = self.database.get_item(USERS_TABLE, username)
            if user:
                new_token = self._generate_jwt(username)
                user["token"] = new_token
                user["modified"] = int(datetime.utcnow().timestamp() * 1000)
                self.database.update_item(USERS_TABLE, username, user)
                logger.info(f"Token refreshed for user {username}.")
                return new_token
        logger.warning("Invalid refresh token provided.")
        return None

    def logout(self, token: str) -> bool:
        """Log out a user by invalidating their token."""
        payload = self._verify_jwt(token)
        if payload:
            username = payload.get("sub")
            user = self.database.get_item(USERS_TABLE, username)
            if user:
                user["token"] = None
                user["modified"] = int(datetime.utcnow().timestamp() * 1000)
                self.database.update_item(USERS_TABLE, username, user)
                logger.info(f"User {username} logged out successfully.")
                return True
        logger.warning("Invalid token provided for logout.")
        return False
