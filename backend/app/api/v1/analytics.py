from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.db_models import Project, LearningEvent
from app.api.v1.deps import verify_project_ownership

router = APIRouter(tags=["Analytics & Events"])

class LearningEventCreate(BaseModel):
    idempotency_key: str = Field(..., min_length=4, max_length=128)
    event_type: str = Field(..., min_length=2, max_length=64)
    payload: Dict[str, Any] = Field(default_factory=dict)

class LearningEventResponse(BaseModel):
    id: str
    idempotency_key: str
    event_type: str
    payload: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/projects/{project_id}/analytics/events", response_model=List[LearningEventResponse])
async def list_project_events(
    project_id: str,
    limit: int = 50,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve immutable learning event timeline for a project."""
    result = await db.execute(
        select(LearningEvent)
        .where(LearningEvent.project_id == project.id)
        .order_by(LearningEvent.created_at.desc())
        .limit(limit)
    )
    events = result.scalars().all()
    return [LearningEventResponse.model_validate(e) for e in events]

@router.post("/projects/{project_id}/analytics/events", response_model=LearningEventResponse, status_code=status.HTTP_201_CREATED)
async def ingest_learning_event(
    project_id: str,
    req: LearningEventCreate,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Idempotently record client learning events (e.g., flashcard viewed, hint clicked, concept bookmarked)."""
    # Check if idempotency_key already exists
    existing_res = await db.execute(
        select(LearningEvent).where(LearningEvent.idempotency_key == req.idempotency_key)
    )
    existing = existing_res.scalars().first()
    if existing:
        return LearningEventResponse.model_validate(existing)

    event = LearningEvent(
        idempotency_key=req.idempotency_key,
        user_id=project.user_id,
        project_id=project.id,
        event_type=req.event_type,
        payload=req.payload
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    return LearningEventResponse.model_validate(event)
