from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    api_title: str = "ContainerGuard Cloud API"
    api_version: str = "2.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: Optional[str] = None
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: list = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
