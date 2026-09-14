import logging
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("study_companion.redis")

_redis_client: Optional[aioredis.Redis] = None

def get_redis_client() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        url = settings.REDIS_URL.replace("localhost", "127.0.0.1")
        _redis_client = aioredis.from_url(
            url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2.0
        )
    return _redis_client

async def close_redis_client():
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None

async def check_redis_health() -> Dict[str, Any]:
    """Health check helper verifying Redis ping connectivity."""
    try:
        client = get_redis_client()
        pong = await client.ping()
        return {
            "status": "connected" if pong else "degraded",
            "ping": pong,
            "url": settings.REDIS_URL.split("@")[-1] if "@" in settings.REDIS_URL else settings.REDIS_URL
        }
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return {
            "status": "disconnected",
            "error": str(e)
        }
