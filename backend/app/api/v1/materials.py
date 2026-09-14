import os
import shutil
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db, async_session_maker
from app.core.config import settings
from app.models.db_models import Project, Material, DocumentChunk, LearningEvent
from app.api.v1.deps import verify_project_ownership, get_current_user
from app.modules.knowledge.service import MaterialIngestionService

router = APIRouter(tags=["Materials"])

class MaterialResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    file_size_bytes: int
    status: str
    page_count: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MaterialStatusResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    status: str
    page_count: int
    chunks_count: int
    error_message: Optional[str]

async def _bg_process_material(material_id: str):
    """Background task runner for asynchronous material parsing and embedding generation."""
    async with async_session_maker() as session:
        await MaterialIngestionService.process_material(material_id, session)

@router.post("/projects/{project_id}/materials/upload", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def upload_material(
    project_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Upload a PDF study material to be indexed, chunked, and embedded into pgvector."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents (.pdf) are currently supported."
        )

    # Save file to project storage directory
    project_storage = os.path.join(settings.STORAGE_PATH, project_id)
    os.makedirs(project_storage, exist_ok=True)
    safe_filename = os.path.basename(file.filename)
    dest_path = os.path.join(project_storage, safe_filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(dest_path)

    # Create Material record
    material = Material(
        project_id=project.id,
        filename=safe_filename,
        file_path=dest_path,
        file_size_bytes=file_size,
        status="QUEUED",
        page_count=0
    )
    db.add(material)
    await db.flush()

    # Record event
    event = LearningEvent(
        idempotency_key=f"upload_{material.id}",
        user_id=project.user_id,
        project_id=project.id,
        event_type="MATERIAL_UPLOADED",
        payload={"filename": safe_filename, "file_size": file_size}
    )
    db.add(event)

    await db.commit()
    await db.refresh(material)

    # Queue background processing
    background_tasks.add_task(_bg_process_material, material.id)

    return MaterialResponse.model_validate(material)

@router.get("/projects/{project_id}/materials", response_model=List[MaterialResponse])
async def list_materials(
    project_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """List all uploaded study materials for the given project."""
    result = await db.execute(
        select(Material).where(Material.project_id == project.id).order_by(Material.created_at.desc())
    )
    materials = result.scalars().all()
    return [MaterialResponse.model_validate(m) for m in materials]

@router.get("/projects/{project_id}/materials/{material_id}/status", response_model=MaterialStatusResponse)
async def get_material_status(
    project_id: str,
    material_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve indexing and embedding status for an uploaded material."""
    result = await db.execute(
        select(Material).where(Material.id == material_id, Material.project_id == project.id)
    )
    material = result.scalars().first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found.")

    chunk_res = await db.execute(
        select(func.count(DocumentChunk.id)).where(DocumentChunk.material_id == material.id)
    )
    chunk_count = chunk_res.scalar() or 0

    return MaterialStatusResponse(
        id=material.id,
        project_id=material.project_id,
        filename=material.filename,
        status=material.status,
        page_count=material.page_count,
        chunks_count=chunk_count,
        error_message=material.error_message
    )

@router.delete("/projects/{project_id}/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    project_id: str,
    material_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Delete a material and its associated vector embeddings and disk files."""
    result = await db.execute(
        select(Material).where(Material.id == material_id, Material.project_id == project.id)
    )
    material = result.scalars().first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found.")

    # Remove file on disk if exists
    if os.path.exists(material.file_path):
        try:
            os.remove(material.file_path)
        except OSError:
            pass

    await db.delete(material)
    await db.commit()
    return None
