"""Application configuration and environment settings."""

from functools import lru_cache
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Find and load .env file from the project root if it exists
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
if _ENV_FILE.exists():
    load_dotenv(dotenv_path=_ENV_FILE)
else:
    load_dotenv()


class Settings:
    """Application settings loaded from environment variables with sensible defaults."""

    def __init__(self) -> None:
        # Database Settings
        self.POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
        self.POSTGRES_DB: str = os.getenv("POSTGRES_DB", "crud_db")
        self.POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
        self.POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.DATABASE_URL: str | None = os.getenv("DATABASE_URL")

        # Connection Pool Settings
        self.DB_POOL_MIN_SIZE: int = int(os.getenv("DB_POOL_MIN_SIZE", "1"))
        self.DB_POOL_MAX_SIZE: int = int(os.getenv("DB_POOL_MAX_SIZE", "10"))
        self.DB_TIMEOUT_SECONDS: float = float(os.getenv("DB_TIMEOUT_SECONDS", "30.0"))

        # Application Settings
        self.APP_NAME: str = os.getenv("APP_NAME", "User Directory CRUD")
        self.APP_VERSION: str = "0.1.0"
        self.APP_ENV: str = os.getenv("APP_ENV", "development")
        self.DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def db_url(self) -> str:
        """Construct or return the PostgreSQL connection URL."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def model_dump(self) -> dict[str, Any]:
        """Return non-sensitive configuration values."""
        return {
            "APP_NAME": self.APP_NAME,
            "APP_VERSION": self.APP_VERSION,
            "APP_ENV": self.APP_ENV,
            "DEBUG": self.DEBUG,
            "HOST": self.HOST,
            "PORT": self.PORT,
            "POSTGRES_HOST": self.POSTGRES_HOST,
            "POSTGRES_PORT": self.POSTGRES_PORT,
            "POSTGRES_DB": self.POSTGRES_DB,
            "DB_POOL_MIN_SIZE": self.DB_POOL_MIN_SIZE,
            "DB_POOL_MAX_SIZE": self.DB_POOL_MAX_SIZE,
        }


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()
