from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.knowledge.models import DocumentChunk
from app.modules.learning.models import Material
from app.core.config import settings

class KnowledgeRetriever:
    """Project-isolated vector retriever enforcing strict boundary checks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve(
        self,
        project_id: str,
        query_vector: List[float],
        top_k: int = settings.RETRIEVAL_TOP_K,
        threshold: float = settings.SIMILARITY_THRESHOLD
    ) -> List[Dict[str, Any]]:
        # Hybrid query joining DocumentChunk with Material to fetch filename & page for citations
        stmt = (
            select(
                DocumentChunk.id,
                DocumentChunk.content,
                DocumentChunk.page_number,
                Material.filename,
                DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
            )
            .join(Material, DocumentChunk.material_id == Material.id)
            .where(DocumentChunk.project_id == project_id)
            .order_by("distance")
            .limit(top_k)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        evidence = []
        for row in rows:
            similarity = 1.0 - (row.distance if row.distance is not None else 1.0)
            if similarity >= threshold:
                evidence.append({
                    "chunk_id": row.id,
                    "content": row.content,
                    "page_number": row.page_number,
                    "filename": row.filename,
                    "similarity": round(similarity, 3)
                })

        return evidence
