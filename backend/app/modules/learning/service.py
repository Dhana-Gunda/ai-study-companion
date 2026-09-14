from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.learning.models import Space, Project, Material
from app.modules.learning.schemas import SpaceCreate, ProjectCreate

class LearningService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_spaces(self, user_id: str) -> List[Space]:
        stmt = select(Space).where(Space.user_id == user_id).order_by(Space.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_space(self, user_id: str, data: SpaceCreate) -> Space:
        space = Space(user_id=user_id, name=data.name, description=data.description)
        self.db.add(space)
        await self.db.commit()
        await self.db.refresh(space)
        return space

    async def list_projects(self, space_id: str, user_id: str) -> List[Project]:
        stmt = select(Project).where(Project.space_id == space_id, Project.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_project(self, user_id: str, data: ProjectCreate) -> Project:
        project = Project(
            space_id=data.space_id,
            user_id=user_id,
            name=data.name,
            description=data.description,
            learning_goal=data.learning_goal
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project
