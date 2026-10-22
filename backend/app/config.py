import os
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# Base backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if it exists and python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=BASE_DIR / ".env")
except ImportError:
    pass


class Settings:
    """Application settings loaded from environment variables with safe defaults."""

    APP_NAME: str = os.getenv("APP_NAME", "DataSense AI")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS origins
    _raw_origins: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self._raw_origins.split(",") if origin.strip()]

    # Database connection string (optional for basic startup & health check)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/datasense_ai",
    )

    # LLM configuration (optional for basic startup & health check)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # Storage paths
    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
    CHARTS_DIR: Path = BASE_DIR / os.getenv("CHARTS_DIR", "generated_charts")


settings = Settings()

# Ensure local directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CHARTS_DIR.mkdir(parents=True, exist_ok=True)
