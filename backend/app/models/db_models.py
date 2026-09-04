import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.created_at")

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=list) # List of cited transcript metadata
    provider = Column(String(64), nullable=False, default="ollama")
    model = Column(String(64), nullable=False, default="llama3.2:3b")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    session = relationship("SessionModel", back_populates="messages")
    artifacts = relationship("ArtifactModel", back_populates="message", cascade="all, delete-orphan")

class ArtifactModel(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(32), nullable=False) # 'markdown' or 'html'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    message = relationship("MessageModel", back_populates="artifacts")

class TranscriptChunkModel(Base):
    __tablename__ = "transcript_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    episode_slug = Column(String(255), nullable=False, index=True)
    episode_title = Column(String(512), nullable=False)
    guest_name = Column(String(255), nullable=False, index=True)
    timestamp_ref = Column(String(64), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    embedding = Column(JSON, nullable=False) # Stores 384-d float list for cross-DB compatibility
