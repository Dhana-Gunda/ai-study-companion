from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List
from app.database import get_db
from app.models.db_models import SessionModel, MessageModel, ArtifactModel
from app.models.schemas import SessionCreate, SessionResponse, SessionDetailResponse

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("", response_model=SessionResponse)
async def create_session(session_in: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Initialize a new conversation session."""
    db_session = SessionModel(title=session_in.title or "New Conversation")
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all user sessions ordered by most recent."""
    stmt = select(SessionModel).order_by(desc(SessionModel.updated_at))
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch session details with complete message and artifact history."""
    stmt = (
        select(SessionModel)
        .where(SessionModel.id == session_id)
        .options(
            selectinload(SessionModel.messages).selectinload(MessageModel.artifacts)
        )
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a session and all associated messages/artifacts."""
    stmt = select(SessionModel).where(SessionModel.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    await db.commit()
    return {"status": "success", "message": f"Session {session_id} deleted"}
