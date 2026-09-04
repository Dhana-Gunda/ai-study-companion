import math
import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.rag.embeddings import get_text_embedding
from app.models.db_models import TranscriptChunkModel
from app.config import settings

logger = logging.getLogger("lenny_assistant.rag.retriever")

class TranscriptRetriever:
    """Hybrid Retriever supporting pgvector cosine similarity and in-memory vectorized search."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[Dict[str, Any]]:
        top_k = top_k or settings.RETRIEVAL_TOP_K
        similarity_threshold = similarity_threshold or settings.SIMILARITY_THRESHOLD

        query_vector = await get_text_embedding(query)

        # Attempt native pgvector cosine search first if using PostgreSQL
        try:
            bind = self.session.bind
            if bind and "postgresql" in str(bind.url):
                query_stmt = text("""
                    SELECT
                        episode_title,
                        guest_name,
                        chunk_text,
                        timestamp_ref,
                        1 - (embedding <=> :vector::vector) AS similarity_score
                    FROM transcript_chunks
                    WHERE 1 - (embedding <=> :vector::vector) >= :threshold
                    ORDER BY similarity_score DESC
                    LIMIT :limit;
                """)
                result = await self.session.execute(
                    query_stmt,
                    {
                        "vector": str(query_vector),
                        "threshold": similarity_threshold,
                        "limit": top_k
                    }
                )
                rows = result.fetchall()
                if rows:
                    return [
                        {
                            "episode": r.episode_title,
                            "guest": r.guest_name,
                            "text": r.chunk_text,
                            "timestamp": r.timestamp_ref,
                            "score": float(r.similarity_score)
                        }
                        for r in rows
                    ]
        except Exception as pg_err:
            logger.debug(f"pgvector query not available or errored: {pg_err}. Using ORM vector matching.")

        # In-memory ORM similarity fallback (Works seamlessly with SQLite and Postgres)
        stmt = select(TranscriptChunkModel)
        result = await self.session.execute(stmt)
        all_chunks = result.scalars().all()

        scored_chunks = []
        for chunk in all_chunks:
            chunk_embedding = chunk.embedding
            if isinstance(chunk_embedding, list):
                score = self._cosine_similarity(query_vector, chunk_embedding)
                if score >= similarity_threshold:
                    scored_chunks.append({
                        "episode": chunk.episode_title,
                        "guest": chunk.guest_name,
                        "text": chunk.chunk_text,
                        "timestamp": chunk.timestamp_ref,
                        "score": round(score, 4)
                    })

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    async def get_total_indexed_chunks(self) -> int:
        try:
            stmt = select(TranscriptChunkModel.id)
            result = await self.session.execute(stmt)
            return len(result.scalars().all())
        except Exception:
            return 0
