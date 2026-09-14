import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON, Index, Boolean
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base
from app.core.config import settings

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(32), default="user", nullable=False)  # "user" or "admin"
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    spaces = relationship("Space", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

class Space(Base):
    __tablename__ = "spaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="spaces")
    projects = relationship("Project", back_populates="space", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    space_id = Column(String(36), ForeignKey("spaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    learning_goal = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="projects")
    space = relationship("Space", back_populates="projects")
    materials = relationship("Material", back_populates="project", cascade="all, delete-orphan")
    concepts = relationship("Concept", back_populates="project", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="project", cascade="all, delete-orphan")
    quizzes = relationship("QuizSession", back_populates="project", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="project", cascade="all, delete-orphan")
    learning_context = relationship("LearningContext", back_populates="project", uselist=False, cascade="all, delete-orphan")

class Material(Base):
    __tablename__ = "materials"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, nullable=True, default=0)
    status = Column(String(32), default="QUEUED", index=True, nullable=False)  # QUEUED, PROCESSING, READY, FAILED
    error_message = Column(Text, nullable=True)
    page_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    project = relationship("Project", back_populates="materials")
    chunks = relationship("DocumentChunk", back_populates="material", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    material_id = Column(String(36), ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    material = relationship("Material", back_populates="chunks")

    __table_args__ = (
        Index("ix_doc_chunks_project_id", "project_id"),
        Index("ix_doc_chunks_material_id", "material_id"),
    )

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    project = relationship("Project", back_populates="concepts")
    mastery = relationship("ConceptMastery", back_populates="concept", cascade="all, delete-orphan")
    snapshots = relationship("MasterySnapshot", back_populates="concept", cascade="all, delete-orphan")

class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    mastery_score = Column(Float, default=0.0, nullable=False)  # 0.0 - 1.0
    confidence_level = Column(Float, default=0.1, nullable=False)
    trend = Column(String(32), default="STABLE", nullable=False)  # IMPROVING, STABLE, ATTENTION
    last_assessed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    concept = relationship("Concept", back_populates="mastery")

    __table_args__ = (
        Index("ix_mastery_project_user", "project_id", "user_id"),
    )

class MasterySnapshot(Base):
    __tablename__ = "mastery_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    concept = relationship("Concept", back_populates="snapshots")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="Study Session")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    project = relationship("Project", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # List of citations [{filename, page_number, similarity}]
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    conversation = relationship("Conversation", back_populates="messages")

class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), default="IN_PROGRESS", nullable=False)  # IN_PROGRESS, COMPLETED
    score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="quizzes")
    questions = relationship("Question", back_populates="session", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(36), ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True, index=True)
    question_type = Column(String(32), nullable=False)  # MCQ, OPEN_ENDED
    prompt = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # List of string options for MCQ
    correct_answer = Column(Text, nullable=True)
    difficulty = Column(String(32), default="medium")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    session = relationship("QuizSession", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete-orphan")

class Answer(Base):
    __tablename__ = "answers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_answer = Column(Text, nullable=False)
    score = Column(Float, nullable=True)  # 0.0 to 1.0
    rubric_evaluation = Column(JSON, nullable=True)  # {understanding_level, strengths, missing_concepts}
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    question = relationship("Question", back_populates="answer")

class LearningContext(Base):
    __tablename__ = "learning_contexts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    state_payload = Column(JSON, default=dict)  # Compact persistent context summary
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    project = relationship("Project", back_populates="learning_context")

class LearningEvent(Base):
    __tablename__ = "learning_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    idempotency_key = Column(String(128), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True, index=True)
    project_id = Column(String(36), nullable=True, index=True)
    feature = Column(String(64), nullable=False, index=True)  # tutor_chat, quiz_gen, rubric_eval
    provider = Column(String(32), nullable=False)  # openai, anthropic, ollama
    model = Column(String(64), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    cost_usd = Column(Float, default=0.0)
    status = Column(String(32), default="SUCCESS", index=True)  # SUCCESS, ERROR, REFUSED_LOW_EVIDENCE
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(64), nullable=False)
    headline = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    cta_label = Column(String(128), nullable=False)
    status = Column(String(32), default="ACTIVE", index=True)  # ACTIVE, COMPLETED, DISMISSED
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    project = relationship("Project", back_populates="recommendations")
