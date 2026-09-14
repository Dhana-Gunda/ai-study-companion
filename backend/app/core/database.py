from __future__ import annotations
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.core.config import settings

logger = logging.getLogger("study_companion.database")

Base = declarative_base()

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

def get_engine() -> AsyncEngine:
    global _engine, _session_factory
    if _engine is not None:
        return _engine

    db_url = settings.effective_db_url

    # Strict architectural requirement: Enforce PostgreSQL only (no silent fallback to SQLite)
    if not ("postgresql" in db_url or "postgres" in db_url):
        error_msg = f"FATAL: Database URL '{db_url}' is not PostgreSQL. Architecture strictly requires PostgreSQL with pgvector."
        logger.error(error_msg)
        raise ValueError(error_msg)

    _engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        pool_pre_ping=True
    )
    _session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )
    logger.info(f"Initialized async PostgreSQL engine: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    return _engine

def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        get_engine()
    assert _session_factory is not None
    return _session_factory

def async_session_maker():
    """Returns a new async session from the session factory."""
    factory = get_session_factory()
    return factory()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining an async database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

async def init_db():
    """Initializes PostgreSQL schemas and validates pgvector extension exists. Fails loudly on error."""
    import app.models  # noqa: F401 - Register all models with Base.metadata
    engine = get_engine()
    async with engine.begin() as conn:
        # Require and enable pgvector
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
        if not result.scalar():
            raise RuntimeError("FATAL: PostgreSQL 'vector' extension (pgvector) is NOT installed or could not be enabled.")
        logger.info("PostgreSQL 'vector' (pgvector) extension verified and enabled.")
        
        await conn.run_sync(Base.metadata.create_all)
        logger.info("PostgreSQL database tables created/verified successfully.")

async def check_db_health() -> Dict[str, Any]:
    """Health check helper verifying PostgreSQL connectivity and pgvector support."""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
            has_pgvector = result.scalar() is not None

            return {
                "status": "connected",
                "dialect": "postgresql",
                "pgvector_enabled": has_pgvector,
                "fallback_mode": False
            }
    except Exception as e:
        logger.error(f"PostgreSQL connection health check failed: {e}")
        return {
            "status": "disconnected",
            "dialect": "postgresql",
            "pgvector_enabled": False,
            "fallback_mode": False,
            "error": str(e)
        }
