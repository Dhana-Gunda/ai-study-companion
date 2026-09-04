from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db, is_sqlite_fallback, engine
from app.rag.retriever import TranscriptRetriever
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import ClaudeProvider, OpenAIProvider
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="Health and Operational Status")
async def get_health_status(db: AsyncSession = Depends(get_db)):
    # 1. Check Database
    db_status = {"connected": False, "mode": "sqlite" if is_sqlite_fallback else "postgresql"}
    try:
        await db.execute(text("SELECT 1"))
        db_status["connected"] = True
    except Exception as e:
        db_status["error"] = str(e)

    # 2. Check Indexed Chunks Count
    retriever = TranscriptRetriever(db)
    chunk_count = await retriever.get_total_indexed_chunks()

    # 3. Check Ollama
    ollama = OllamaProvider()
    ollama_status = await ollama.check_health()

    # 4. Check Cloud Providers
    claude = ClaudeProvider()
    openai_prov = OpenAIProvider()
    claude_status = await claude.check_health()
    openai_status = await openai_prov.check_health()

    return {
        "status": "healthy" if db_status["connected"] else "degraded",
        "database": db_status,
        "ollama": ollama_status,
        "cloud_providers": {
            "anthropic": claude_status,
            "openai": openai_status
        },
        "default_provider": settings.DEFAULT_PROVIDER,
        "indexed_chunks": chunk_count,
        "version": "1.0.0"
    }
