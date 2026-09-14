from typing import List, Optional, Any, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.db_models import (
    User, Space, Project, Material, Concept, ConceptMastery,
    LearningEvent, Recommendation, LearningContext
)
from app.api.v1.deps import get_current_user, verify_project_ownership, verify_space_ownership

router = APIRouter(tags=["Projects"])

class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    learning_goal: str = Field(..., min_length=3, description="Target skill or learning objective")

class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    learning_goal: Optional[str] = Field(None, min_length=3)

class ProjectDetailResponse(BaseModel):
    id: str
    space_id: str
    user_id: str
    name: str
    description: Optional[str]
    learning_goal: str
    created_at: datetime
    updated_at: datetime
    materials_count: int = 0
    concepts_count: int = 0

    class Config:
        from_attributes = True

class ProjectDashboardResponse(BaseModel):
    project: ProjectDetailResponse
    overall_mastery_percentage: float
    materials_count: int
    concepts_count: int
    weak_concepts: List[Dict[str, Any]]
    recent_events: List[Dict[str, Any]]
    active_recommendation: Optional[Dict[str, Any]]
    learning_context: Dict[str, Any]

@router.get("/projects", response_model=List[ProjectDetailResponse])
async def list_all_user_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all projects across all spaces owned by the current user."""
    query = (
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
    )
    result = await db.execute(query)
    projects = result.scalars().all()

    output = []
    for p in projects:
        m_count = (await db.execute(select(func.count(Material.id)).where(Material.project_id == p.id))).scalar() or 0
        c_count = (await db.execute(select(func.count(Concept.id)).where(Concept.project_id == p.id))).scalar() or 0
        output.append(
            ProjectDetailResponse(
                id=p.id,
                space_id=p.space_id,
                user_id=p.user_id,
                name=p.name,
                description=p.description,
                learning_goal=p.learning_goal,
                created_at=p.created_at,
                updated_at=p.updated_at,
                materials_count=m_count,
                concepts_count=c_count
            )
        )
    return output

@router.get("/spaces/{space_id}/projects", response_model=List[ProjectDetailResponse])
async def list_projects_in_space(
    space_id: str,
    space: Space = Depends(verify_space_ownership),
    db: AsyncSession = Depends(get_db)
):
    """List all projects within a specific space."""
    query = (
        select(Project)
        .where(Project.space_id == space.id)
        .order_by(Project.created_at.desc())
    )
    result = await db.execute(query)
    projects = result.scalars().all()

    output = []
    for p in projects:
        m_count = (await db.execute(select(func.count(Material.id)).where(Material.project_id == p.id))).scalar() or 0
        c_count = (await db.execute(select(func.count(Concept.id)).where(Concept.project_id == p.id))).scalar() or 0
        output.append(
            ProjectDetailResponse(
                id=p.id,
                space_id=p.space_id,
                user_id=p.user_id,
                name=p.name,
                description=p.description,
                learning_goal=p.learning_goal,
                created_at=p.created_at,
                updated_at=p.updated_at,
                materials_count=m_count,
                concepts_count=c_count
            )
        )
    return output

@router.post("/spaces/{space_id}/projects", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_project_in_space(
    space_id: str,
    req: ProjectCreateRequest,
    space: Space = Depends(verify_space_ownership),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new study project inside the specified space."""
    project = Project(
        space_id=space.id,
        user_id=current_user.id,
        name=req.name.strip(),
        description=req.description.strip() if req.description else None,
        learning_goal=req.learning_goal.strip()
    )
    db.add(project)
    await db.flush()

    # Create initial LearningContext
    learning_context = LearningContext(
        project_id=project.id,
        user_id=current_user.id,
        state_payload={
            "goals": [project.learning_goal],
            "strengths": [],
            "weak_concepts": [],
            "repeated_mistakes": [],
            "summary": f"Initial learning workspace configured for '{project.name}'."
        }
    )
    db.add(learning_context)

    # Emit initial LearningEvent
    event = LearningEvent(
        idempotency_key=f"init_project_{project.id}",
        user_id=current_user.id,
        project_id=project.id,
        event_type="PROJECT_CREATED",
        payload={"project_name": project.name, "space_id": space.id}
    )
    db.add(event)

    await db.commit()
    await db.refresh(project)

    return ProjectDetailResponse(
        id=project.id,
        space_id=project.space_id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        learning_goal=project.learning_goal,
        created_at=project.created_at,
        updated_at=project.updated_at,
        materials_count=0,
        concepts_count=0
    )

@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Get project details."""
    m_count = (await db.execute(select(func.count(Material.id)).where(Material.project_id == project.id))).scalar() or 0
    c_count = (await db.execute(select(func.count(Concept.id)).where(Concept.project_id == project.id))).scalar() or 0

    return ProjectDetailResponse(
        id=project.id,
        space_id=project.space_id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        learning_goal=project.learning_goal,
        created_at=project.created_at,
        updated_at=project.updated_at,
        materials_count=m_count,
        concepts_count=c_count
    )

@router.put("/projects/{project_id}", response_model=ProjectDetailResponse)
async def update_project(
    project_id: str,
    req: ProjectUpdateRequest,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Update project name, description, or learning goal."""
    if req.name is not None:
        project.name = req.name.strip()
    if req.description is not None:
        project.description = req.description.strip()
    if req.learning_goal is not None:
        project.learning_goal = req.learning_goal.strip()

    await db.commit()
    await db.refresh(project)

    m_count = (await db.execute(select(func.count(Material.id)).where(Material.project_id == project.id))).scalar() or 0
    c_count = (await db.execute(select(func.count(Concept.id)).where(Concept.project_id == project.id))).scalar() or 0

    return ProjectDetailResponse(
        id=project.id,
        space_id=project.space_id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        learning_goal=project.learning_goal,
        created_at=project.created_at,
        updated_at=project.updated_at,
        materials_count=m_count,
        concepts_count=c_count
    )

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project and all associated materials, concepts, quizzes, and embeddings."""
    await db.delete(project)
    await db.commit()
    return None

@router.get("/projects/{project_id}/dashboard", response_model=ProjectDashboardResponse)
async def get_project_dashboard(
    project_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Aggregated project dashboard with mastery curve, weak concepts, activity timeline, and next-action recommendation."""
    # 1. Counts
    m_count = (await db.execute(select(func.count(Material.id)).where(Material.project_id == project.id))).scalar() or 0
    c_count = (await db.execute(select(func.count(Concept.id)).where(Concept.project_id == project.id))).scalar() or 0

    # 2. Mastery scores & weak concepts
    mastery_query = (
        select(ConceptMastery, Concept.name)
        .join(Concept, Concept.id == ConceptMastery.concept_id)
        .where(ConceptMastery.project_id == project.id)
    )
    mastery_rows = (await db.execute(mastery_query)).all()

    total_score = 0.0
    weak_concepts = []
    for cm, c_name in mastery_rows:
        total_score += cm.mastery_score
        if cm.trend == "ATTENTION" or cm.mastery_score < 0.60:
            weak_concepts.append({
                "concept_id": cm.concept_id,
                "name": c_name,
                "score": round(cm.mastery_score, 2),
                "trend": cm.trend,
                "confidence": round(cm.confidence_level, 2)
            })

    avg_mastery = (total_score / len(mastery_rows) * 100) if mastery_rows else 0.0

    # 3. Recent events
    events_res = await db.execute(
        select(LearningEvent)
        .where(LearningEvent.project_id == project.id)
        .order_by(LearningEvent.created_at.desc())
        .limit(5)
    )
    recent_events = [
        {
            "id": e.id,
            "event_type": e.event_type,
            "payload": e.payload,
            "created_at": e.created_at.isoformat()
        }
        for e in events_res.scalars().all()
    ]

    # 4. Active recommendation
    rec_res = await db.execute(
        select(Recommendation)
        .where(Recommendation.project_id == project.id, Recommendation.status == "ACTIVE")
        .order_by(Recommendation.created_at.desc())
    )
    rec = rec_res.scalars().first()
    active_rec = None
    if rec:
        active_rec = {
            "id": rec.id,
            "action_type": rec.action_type,
            "headline": rec.headline,
            "description": rec.description,
            "cta_label": rec.cta_label,
            "status": rec.status
        }

    # 5. Learning context
    lc_res = await db.execute(
        select(LearningContext).where(LearningContext.project_id == project.id)
    )
    lc = lc_res.scalars().first()
    lc_payload = lc.state_payload if lc else {}

    proj_detail = ProjectDetailResponse(
        id=project.id,
        space_id=project.space_id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        learning_goal=project.learning_goal,
        created_at=project.created_at,
        updated_at=project.updated_at,
        materials_count=m_count,
        concepts_count=c_count
    )

    return ProjectDashboardResponse(
        project=proj_detail,
        overall_mastery_percentage=round(avg_mastery, 1),
        materials_count=m_count,
        concepts_count=c_count,
        weak_concepts=weak_concepts,
        recent_events=recent_events,
        active_recommendation=active_rec,
        learning_context=lc_payload
    )
