from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.modules.analytics.models import AIRequestLog, LearningEvent

class AdminMetricsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview_metrics(self) -> Dict[str, Any]:
        # Aggregate AI tokens and total requests
        total_ai_stmt = select(func.count(AIRequestLog.id), func.sum(AIRequestLog.cost_usd))
        ai_res = await self.db.execute(total_ai_stmt)
        ai_count, total_cost = ai_res.first() or (0, 0.0)

        total_events_stmt = select(func.count(LearningEvent.id))
        event_res = await self.db.execute(total_events_stmt)
        event_count = event_res.scalar() or 0

        return {
            "total_ai_invocations": ai_count or 0,
            "total_ai_cost_usd": round(total_cost or 0.0, 4),
            "total_learning_events": event_count or 0,
            "system_health": "OPTIMAL"
        }
