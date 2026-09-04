from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class Citation(BaseModel):
    episode: str
    guest: str
    text: str
    timestamp: Optional[str] = None
    score: float = 0.0

class ArtifactBase(BaseModel):
    title: str
    artifact_type: str = "markdown" # 'markdown' or 'html'
    content: str

class ArtifactCreate(ArtifactBase):
    message_id: str

class ArtifactResponse(ArtifactBase):
    id: str
    message_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    provider: Optional[str] = "ollama"
    model: Optional[str] = "llama3.2:3b"

class MessageCreate(MessageBase):
    session_id: str

class MessageResponse(MessageBase):
    id: str
    session_id: str
    created_at: datetime
    artifacts: List[ArtifactResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    title: Optional[str] = "New Conversation"

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SessionDetailResponse(SessionResponse):
    messages: List[MessageResponse] = Field(default_factory=list)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    mode: Optional[str] = "default"  # 'default', 'ship30', or 'artifact'
    provider: Optional[str] = "ollama" # 'ollama', 'claude', 'openai'
    model: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    database: Dict[str, Any]
    ollama: Dict[str, Any]
    cloud_providers: Dict[str, Any]
    indexed_chunks: int
    version: str = "1.0.0"
