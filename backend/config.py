from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    gemini_api_key: str = ""
    groq_api_key: str = ""
    ai_provider: str = "gemini"  # "gemini" | "groq"
    groq_model: str = "gemma2-9b-it"  # or "llama-3.1-8b-instant", "llama-3.3-70b-versatile"
    secret_key: str = "changeme-super-secret-key-in-production"
    database_url: str = "sqlite+aiosqlite:///./studysmart.db"
    access_token_expire_minutes: int = 10080  # 7 days
    algorithm: str = "HS256"
    app_name: str = "StudySmart AI"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
