import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Lenny Growth Assistant"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password123@localhost:5432/lenny_assistant"
    SQLITE_FALLBACK_URL: str = "sqlite+aiosqlite:///./lenny_assistant.db"
    
    # Local LLM (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    
    # Cloud LLM (Anthropic & OpenAI)
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    
    # Default Provider: "ollama", "claude", or "openai"
    DEFAULT_PROVIDER: str = "ollama"
    
    # Retrieval Hyperparameters
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.60
    EMBEDDING_DIMENSION: int = 384
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

def get_settings() -> Settings:
    return settings
