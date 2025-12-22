"""Configuration management for Stitch Engine"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Anthropic API
    anthropic_api_key: str
    anthropic_model: str = "claude-opus-4-5-20251101"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Storage
    upload_dir: Path = Path("./uploads")
    temp_dir: Path = Path("./temp")

    # Processing limits
    max_image_size_mb: int = 10
    max_image_dimension: int = 4096

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings singleton"""
    return Settings()
