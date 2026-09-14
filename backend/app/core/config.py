import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Study Companion"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database URLs (Support both DB_URL and DATABASE_URL)
    DB_URL: Optional[str] = None
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password123@localhost:5432/study_companion"

    # Redis URL
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security & Auth
    JWT_SECRET: str = "dev-secret-key-change-in-production-12345"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # AI Providers
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    DEFAULT_PROVIDER: str = "openai"

    # Local Ollama Fallback
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"

    # Storage Path for Uploaded Learning Materials
    STORAGE_PATH: str = "./storage/materials"

    # Vector Search Settings
    EMBEDDING_DIMENSION: int = 1536  # Default OpenAI text-embedding-3-small
    SIMILARITY_THRESHOLD: float = 0.65
    RETRIEVAL_TOP_K: int = 4

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    @property
    def effective_db_url(self) -> str:
        """Prefers DB_URL if explicitly provided, else DATABASE_URL."""
        return self.DB_URL if self.DB_URL else self.DATABASE_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

def get_settings() -> Settings:
    return settings
