from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.analytics.models import LearningEvent

class EventDispatcher:
    """Publishes domain learning events to PostgreSQL and triggers background side-effects."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def dispatch(self, event_type: str, user_id: str, project_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None):
        event = LearningEvent(
            event_type=event_type,
            user_id=user_id,
            project_id=project_id,
            payload=payload or {}
        )
        self.db.add(event)
        await self.db.commit()
