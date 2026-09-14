from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.modules.analytics.models import LearningEvent

class AnalyticsTracker:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        stmt = select(func.count(LearningEvent.id)).where(LearningEvent.project_id == project_id)
        result = await self.db.execute(stmt)
        total_events = result.scalar() or 0
        return {
            "project_id": project_id,
            "total_events": total_events
        }
