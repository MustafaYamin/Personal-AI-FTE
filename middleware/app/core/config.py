from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    debug: bool = True

    # Phase 4 wires this up to call the backend for task/policy/approval data.
    backend_api_url: str = "http://backend:8000/api/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
