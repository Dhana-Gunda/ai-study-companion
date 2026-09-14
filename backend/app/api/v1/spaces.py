from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.db_models import User, Space, Project
from app.api.v1.deps import get_current_user, verify_space_ownership

router = APIRouter(prefix="/spaces", tags=["Spaces"])

class SpaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class SpaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class SpaceDetailResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    user_id: str
    projects_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[SpaceDetailResponse])
async def list_spaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all learning spaces owned by the current user."""
    # Query spaces and compute project count per space
    query = (
        select(Space, func.count(Project.id).label("projects_count"))
        .outerjoin(Project, Project.space_id == Space.id)
        .where(Space.user_id == current_user.id)
        .group_by(Space.id)
        .order_by(Space.created_at.desc())
    )
    result = await db.execute(query)
    rows = result.all()

    output = []
    for space, p_count in rows:
        resp = SpaceDetailResponse(
            id=space.id,
            name=space.name,
            description=space.description,
            user_id=space.user_id,
            projects_count=p_count,
            created_at=space.created_at,
            updated_at=space.updated_at
        )
        output.append(resp)
    return output

@router.post("", response_model=SpaceDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_space(
    req: SpaceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new top-level learning space for the current user."""
    space = Space(
        user_id=current_user.id,
        name=req.name.strip(),
        description=req.description.strip() if req.description else None
    )
    db.add(space)
    await db.commit()
    await db.refresh(space)

    return SpaceDetailResponse(
        id=space.id,
        name=space.name,
        description=space.description,
        user_id=space.user_id,
        projects_count=0,
        created_at=space.created_at,
        updated_at=space.updated_at
    )

@router.get("/{space_id}", response_model=SpaceDetailResponse)
async def get_space(
    space_id: str,
    space: Space = Depends(verify_space_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific space owned by current user."""
    count_res = await db.execute(select(func.count(Project.id)).where(Project.space_id == space.id))
    p_count = count_res.scalar() or 0

    return SpaceDetailResponse(
        id=space.id,
        name=space.name,
        description=space.description,
        user_id=space.user_id,
        projects_count=p_count,
        created_at=space.created_at,
        updated_at=space.updated_at
    )

@router.put("/{space_id}", response_model=SpaceDetailResponse)
async def update_space(
    space_id: str,
    req: SpaceUpdateRequest,
    space: Space = Depends(verify_space_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Update a space's name or description."""
    if req.name is not None:
        space.name = req.name.strip()
    if req.description is not None:
        space.description = req.description.strip()

    await db.commit()
    await db.refresh(space)

    count_res = await db.execute(select(func.count(Project.id)).where(Project.space_id == space.id))
    p_count = count_res.scalar() or 0

    return SpaceDetailResponse(
        id=space.id,
        name=space.name,
        description=space.description,
        user_id=space.user_id,
        projects_count=p_count,
        created_at=space.created_at,
        updated_at=space.updated_at
    )

@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_space(
    space_id: str,
    space: Space = Depends(verify_space_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Delete a space and all associated projects (cascade)."""
    await db.delete(space)
    await db.commit()
    return None
