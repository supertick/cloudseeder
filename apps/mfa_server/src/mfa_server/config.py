from pydantic_settings import BaseSettings
from mfa_server.models.config import Config

class AppSettings(Config, BaseSettings):
    class Config:
        env_prefix = "MFA_SERVER_"  # Looks for env variables like AI_CORE_PORT
        env_file = ".env"  # Optional: Load from .env file

    def to_config(self) -> Config:
        """Convert AppSettings to the original Config model."""
        return Config(**self.dict())

# Instantiate settings (loads from env variables)
settings = AppSettings()

# Optional: Convert to the original Config model
config = settings.to_config()
