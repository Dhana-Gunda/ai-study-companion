import time
from datetime import datetime, timezone
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import check_db_health
from app.core.redis import check_redis_health

router = APIRouter()

@router.get("/health", summary="System Health & Connectivity Probe")
async def get_health_status():
    start_time = time.time()
    
    # Check DB and Redis concurrently
    db_health = await check_db_health()
    redis_health = await check_redis_health()

    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    is_db_ok = db_health.get("status") == "connected"
    is_redis_ok = redis_health.get("status") == "connected"

    overall_status = "healthy" if (is_db_ok and is_redis_ok) else ("degraded" if is_db_ok else "unhealthy")
    status_code = status.HTTP_200_OK if is_db_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    payload = {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latency_ms": latency_ms,
        "services": {
            "database": db_health,
            "redis": redis_health,
            "ai_providers": {
                "openai": {"configured": bool(settings.OPENAI_API_KEY), "model": settings.OPENAI_MODEL},
                "anthropic": {"configured": bool(settings.ANTHROPIC_API_KEY), "model": settings.ANTHROPIC_MODEL},
                "default_provider": settings.DEFAULT_PROVIDER,
            }
        },
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }
    return JSONResponse(status_code=status_code, content=payload)
