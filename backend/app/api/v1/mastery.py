from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.db_models import Project, Concept, ConceptMastery, MasterySnapshot, Recommendation
from app.api.v1.deps import verify_project_ownership

router = APIRouter(tags=["Mastery & Growth"])

class ConceptMasteryResponse(BaseModel):
    concept_id: str
    name: str
    description: Optional[str]
    mastery_score: float
    confidence_level: float
    trend: str
    last_assessed_at: Optional[datetime]

class SnapshotPoint(BaseModel):
    recorded_at: datetime
    score: float

class ConceptHistoryResponse(BaseModel):
    concept_id: str
    name: str
    history: List[SnapshotPoint]

class RecommendationResponse(BaseModel):
    id: str
    action_type: str
    headline: str
    description: str
    cta_label: str
    status: str
    created_at: datetime

@router.get("/projects/{project_id}/mastery", response_model=List[ConceptMasteryResponse])
async def get_project_mastery(
    project_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve concept mastery scores, confidence levels, and learning trends for a project."""
    query = (
        select(Concept, ConceptMastery)
        .outerjoin(ConceptMastery, ConceptMastery.concept_id == Concept.id)
        .where(Concept.project_id == project.id)
    )
    result = await db.execute(query)
    rows = result.all()

    output = []
    for concept, mastery in rows:
        output.append(
            ConceptMasteryResponse(
                concept_id=concept.id,
                name=concept.name,
                description=concept.description,
                mastery_score=mastery.mastery_score if mastery else 0.0,
                confidence_level=mastery.confidence_level if mastery else 0.1,
                trend=mastery.trend if mastery else "STABLE",
                last_assessed_at=mastery.last_assessed_at if mastery else None
            )
        )
    return output

@router.get("/projects/{project_id}/mastery/history", response_model=List[ConceptHistoryResponse])
async def get_mastery_history(
    project_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve historical mastery snapshot curves for growth analysis and charting."""
    c_res = await db.execute(select(Concept).where(Concept.project_id == project.id))
    concepts = c_res.scalars().all()

    output = []
    for c in concepts:
        snap_res = await db.execute(
            select(MasterySnapshot)
            .where(MasterySnapshot.concept_id == c.id, MasterySnapshot.project_id == project.id)
            .order_by(MasterySnapshot.recorded_at.asc())
        )
        snapshots = snap_res.scalars().all()
        points = [SnapshotPoint(recorded_at=s.recorded_at, score=s.score) for s in snapshots]
        output.append(
            ConceptHistoryResponse(
                concept_id=c.id,
                name=c.name,
                history=points
            )
        )
    return output

@router.get("/projects/{project_id}/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    project_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve active and recent pedagogical recommendations answering 'What should I do next?'."""
    rec_res = await db.execute(
        select(Recommendation)
        .where(Recommendation.project_id == project.id)
        .order_by(Recommendation.created_at.desc())
    )
    recs = rec_res.scalars().all()
    return [
        RecommendationResponse(
            id=r.id,
            action_type=r.action_type,
            headline=r.headline,
            description=r.description,
            cta_label=r.cta_label,
            status=r.status,
            created_at=r.created_at
        )
        for r in recs
    ]
