from typing import Dict
from pydantic_settings import BaseSettings
from ai_core.models.config import Config
from dotenv import load_dotenv

load_dotenv(".env")
class AppSettings(Config, BaseSettings):
    class Config:
        env_prefix = "AI_CORE_"  # Looks for env variables like AI_CORE_PORT
        env_file = ".env"  # Optional: Load from .env file
        extra = "ignore"  # Ignore extra env variables

    def to_config(self) -> Config:
        """Convert AppSettings to the original Config model."""
        return Config(**self.dict())

# Instantiate settings (loads from env variables)
settings = AppSettings()

# Optional: Convert to the original Config model
config = settings.to_config()

def config_provider() -> Dict[str, str]:
    return settings.dict()
