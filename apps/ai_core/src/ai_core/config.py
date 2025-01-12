from pydantic_settings import BaseSettings
from ai_core.models.config import Config

class AppSettings(BaseSettings):
    id: str
    port: int
    work_dir: str
    log_level: str
    deepgram_api_key: str

    class Config:
        env_prefix = "AI_CORE_"  # Looks for env variables like AI_CORE_PORT
        env_file = ".env"  # Optional: Load from .env file

    def to_config(self) -> Config:
        """Convert AppSettings to the original Config model."""
        return Config(**self.dict())

# Instantiate settings (loads from env variables)
settings = AppSettings()

# Optional: Convert to the original Config model
config = settings.to_config()
