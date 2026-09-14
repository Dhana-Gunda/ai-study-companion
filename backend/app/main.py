import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.redis import close_redis_client
from app.core.logging import setup_logging
from app.api.v1.router import api_router

# Setup structured logging
setup_logging()
logger = logging.getLogger("study_companion.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing DB initialization and clean resource teardown."""
    import asyncio
    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}...")
    try:
        await asyncio.wait_for(init_db(), timeout=5.0)
        logger.info("Database schemas and pgvector extension verified.")
    except Exception as e:
        logger.warning(f"Startup DB initialization notice (app will continue): {e}")
    yield
    logger.info("Shutting down application resources...")
    try:
        await close_redis_client()
    except Exception:
        pass
    logger.info("Teardown complete.")

def create_app() -> FastAPI:
    """FastAPI application factory with middleware and exception handling."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="AI-powered learning and growth workspace with grounded RAG, adaptive assessments, and mastery tracking.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Cross-Origin Resource Sharing (CORS)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API v1 routes
    application.include_router(api_router, prefix=settings.API_V1_STR)

    @application.get("/", tags=["Root"])
    async def root():
        return {
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs": "/docs",
            "health": f"{settings.API_V1_STR}/health"
        }

    # Global Exception Handler
    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception at {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "https://errors.studycompanion.internal/internal-server-error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": str(exc),
                "path": str(request.url.path)
            }
        )

    return application

app = create_app()
