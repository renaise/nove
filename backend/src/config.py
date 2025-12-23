"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/novia"

    # AWS S3
    aws_region: str = "us-east-1"
    s3_bucket: str = "novia-assets"

    # Gemini API (Nano Banana Pro)
    gemini_api_key: str = ""

    # SAM-3D-Body
    sam3d_checkpoint_path: str = "./checkpoints/sam-3d-body-dinov3/model.ckpt"
    mhr_model_path: str = "./checkpoints/sam-3d-body-dinov3/assets/mhr_model.pt"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    model_config = {"env_prefix": "NOVIA_", "env_file": ".env"}


settings = Settings()
