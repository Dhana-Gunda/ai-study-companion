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
    DATABASE_URL: str = "postgresql+asyncpg://neondb_owner:npg_o3cAnKWSxZ0m@ep-red-glade-ayl3bdrs.c-5.us-east-2.aws.neon.tech/neondb"

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
        "https://ai-study-companion-gamma.vercel.app",
        "*"
    ]

    @property
    def effective_db_url(self) -> str:
        """Prefers env var DATABASE_URL or DB_URL, normalizing for asyncpg."""
        import os, re
        neon_fallback = "postgresql+asyncpg://neondb_owner:npg_o3cAnKWSxZ0m@ep-red-glade-ayl3bdrs.c-5.us-east-2.aws.neon.tech/neondb"
        raw = os.environ.get("DATABASE_URL") or os.environ.get("DB_URL") or self.DB_URL or self.DATABASE_URL or neon_fallback
        url = str(raw).strip()
        
        # If in production and pointing to localhost, enforce Neon fallback
        if "localhost" in url and (self.ENVIRONMENT == "production" or os.environ.get("ENVIRONMENT") == "production"):
            url = neon_fallback
            
        # Ensure postgresql+asyncpg driver prefix
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
        # Remove query params that asyncpg does not support
        if "channel_binding=" in url:
            url = re.sub(r"[?&]channel_binding=[^&]+", "", url)
            if "?" not in url and "&" in url:
                url = url.replace("&", "?", 1)
                
        return url

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

def get_settings() -> Settings:
    return settings
