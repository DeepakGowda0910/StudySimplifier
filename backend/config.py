from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    gemini_api_key: str = ""
    secret_key: str = "changeme-super-secret-key-in-production"
    database_url: str = "sqlite+aiosqlite:///./studysmart.db"
    access_token_expire_minutes: int = 10080  # 7 days
    algorithm: str = "HS256"
    app_name: str = "StudySmart AI"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
