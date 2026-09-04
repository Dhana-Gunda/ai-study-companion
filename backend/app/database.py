import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.config import settings

logger = logging.getLogger("lenny_assistant.database")

Base = declarative_base()

# Determine database engine (PostgreSQL or SQLite Fallback)
engine = None
async_session_factory = None
is_sqlite_fallback = False

def create_engine_instance(db_url: str):
    connect_args = {}
    if "sqlite" in db_url:
        connect_args = {"check_same_thread": False}
    return create_async_engine(
        db_url,
        echo=False,
        future=True,
        connect_args=connect_args
    )

try:
    engine = create_engine_instance(settings.DATABASE_URL)
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
except Exception as e:
    logger.warning(f"Failed to create engine with primary URL: {e}. Falling back to SQLite.")
    engine = create_engine_instance(settings.SQLITE_FALLBACK_URL)
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    is_sqlite_fallback = True

async def get_db() -> AsyncSession:
    """FastAPI dependency for yielding async database sessions."""
    global engine, async_session_factory, is_sqlite_fallback
    try:
        async with async_session_factory() as session:
            yield session
    except Exception as e:
        # If Postgres fails during execution, attempt switch to SQLite
        if not is_sqlite_fallback and "postgres" in settings.DATABASE_URL:
            logger.error(f"Database connection error: {e}. Switching to SQLite fallback.")
            engine = create_engine_instance(settings.SQLITE_FALLBACK_URL)
            async_session_factory = async_sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            is_sqlite_fallback = True
            async with async_session_factory() as session:
                yield session
        else:
            raise e

async def init_db():
    """Create all tables and required extensions."""
    global engine, async_session_factory, is_sqlite_fallback
    try:
        async with engine.begin() as conn:
            if not is_sqlite_fallback and "postgresql" in str(engine.url):
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    logger.info("pgvector extension initialized.")
                except Exception as ext_err:
                    logger.warning(f"Could not initialize pgvector extension: {ext_err}")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.warning(f"Database initialization with primary URL failed: {e}. Switching to SQLite fallback.")
        engine = create_engine_instance(settings.SQLITE_FALLBACK_URL)
        async_session_factory = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        is_sqlite_fallback = True
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("SQLite fallback tables initialized successfully.")
