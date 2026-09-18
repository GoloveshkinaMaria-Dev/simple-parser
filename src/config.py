from pathlib import Path

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8-sig",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn
    ENVIRONMENT: str = "local"


settings = Config()
