from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class SpaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class SpaceCreate(SpaceBase):
    pass

class SpaceOut(SpaceBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    learning_goal: str = Field(..., min_length=3)

class ProjectCreate(ProjectBase):
    space_id: str

class ProjectOut(ProjectBase):
    id: str
    space_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MaterialOut(BaseModel):
    id: str
    project_id: str
    filename: str
    status: str
    page_count: Optional[str] = "0"
    created_at: datetime

    class Config:
        from_attributes = True
