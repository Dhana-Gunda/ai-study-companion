from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db, check_db_health
from app.core.redis import check_redis_health
from app.models.db_models import User, Space, Project, AIRequestLog
from app.api.v1.deps import get_current_active_admin

router = APIRouter(prefix="/admin", tags=["Admin & Observability"])

class AdminUserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    spaces_count: int
    projects_count: int
    created_at: datetime

class AIMetricsSummary(BaseModel):
    total_requests: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost_usd: float
    avg_latency_ms: float
    p95_latency_ms: float
    refusal_count: int
    refusal_rate_percentage: float
    requests_by_feature: Dict[str, int]
    recent_logs: List[Dict[str, Any]]

class AdminHealthResponse(BaseModel):
    status: str
    database: Dict[str, Any]
    redis: Dict[str, Any]
    timestamp: datetime

@router.get("/users", response_model=List[AdminUserResponse])
async def list_admin_users(
    admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin-only: list all registered platform users with spaces and projects metrics."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()

    output = []
    for u in users:
        s_count = (await db.execute(select(func.count(Space.id)).where(Space.user_id == u.id))).scalar() or 0
        p_count = (await db.execute(select(func.count(Project.id)).where(Project.user_id == u.id))).scalar() or 0
        output.append(
            AdminUserResponse(
                id=u.id,
                email=u.email,
                name=u.name,
                role=u.role,
                spaces_count=s_count,
                projects_count=p_count,
                created_at=u.created_at
            )
        )
    return output

@router.get("/ai-metrics", response_model=AIMetricsSummary)
async def get_ai_metrics(
    admin: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin-only: fine-grained LLM observability, spend calculation, latency percentiles, and refusal metrics."""
    result = await db.execute(select(AIRequestLog).order_by(AIRequestLog.created_at.desc()))
    logs = result.scalars().all()

    total_reqs = len(logs)
    total_prompt = sum(l.prompt_tokens or 0 for l in logs)
    total_comp = sum(l.completion_tokens or 0 for l in logs)
    total_cost = sum(l.cost_usd or 0.0 for l in logs)
    latencies = sorted([l.latency_ms for l in logs if l.latency_ms is not None])

    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
    p95_index = int(0.95 * len(latencies))
    p95_latency = latencies[p95_index] if latencies else 0.0

    refusals = [l for l in logs if l.status == "REFUSED_LOW_EVIDENCE"]
    refusal_count = len(refusals)
    refusal_rate = (refusal_count / total_reqs * 100) if total_reqs > 0 else 0.0

    by_feature: Dict[str, int] = {}
    for l in logs:
        by_feature[l.feature] = by_feature.get(l.feature, 0) + 1

    recent_logs = [
        {
            "id": l.id,
            "feature": l.feature,
            "provider": l.provider,
            "model": l.model,
            "prompt_tokens": l.prompt_tokens,
            "completion_tokens": l.completion_tokens,
            "latency_ms": l.latency_ms,
            "cost_usd": l.cost_usd,
            "status": l.status,
            "error_message": l.error_message,
            "created_at": l.created_at.isoformat()
        }
        for l in logs[:15]
    ]

    return AIMetricsSummary(
        total_requests=total_reqs,
        total_prompt_tokens=total_prompt,
        total_completion_tokens=total_comp,
        total_cost_usd=round(total_cost, 4),
        avg_latency_ms=round(avg_latency, 2),
        p95_latency_ms=round(p95_latency, 2),
        refusal_count=refusal_count,
        refusal_rate_percentage=round(refusal_rate, 2),
        requests_by_feature=by_feature,
        recent_logs=recent_logs
    )

@router.get("/health", response_model=AdminHealthResponse)
async def get_admin_system_health(
    admin: User = Depends(get_current_active_admin)
):
    """Admin-only: system services health status and diagnostic checks."""
    db_health = await check_db_health()
    redis_health = await check_redis_health()
    is_healthy = (db_health.get("status") == "connected" and redis_health.get("status") == "connected")

    return AdminHealthResponse(
        status="healthy" if is_healthy else "degraded",
        database=db_health,
        redis=redis_health,
        timestamp=datetime.utcnow()
    )
