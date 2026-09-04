import pytest
import math
from app.rag.chunker import chunker
from app.rag.embeddings import get_text_embedding
from app.rag.retriever import TranscriptRetriever
from app.database import async_session_factory, init_db
from app.models.db_models import TranscriptChunkModel

def test_chunker_dialogue_preservation():
    sample_text = """
(00:01:00) Lenny: Welcome to the show.
(00:01:20) Elena Verna: Thanks Lenny. Let's discuss Product-Led Growth and freemium.
(00:05:00) Lenny: How do you choose between free trial and freemium?
"""
    chunks = chunker.chunk_transcript(
        text=sample_text,
        episode_title="PLG Deep Dive",
        guest_name="Elena Verna",
        episode_slug="elena-verna-plg"
    )
    assert len(chunks) >= 1
    first_chunk = chunks[0]
    assert "Elena Verna" in first_chunk["chunk_text"]
    assert "PLG Deep Dive" in first_chunk["chunk_text"]
    assert first_chunk["guest_name"] == "Elena Verna"

@pytest.mark.asyncio
async def test_embedding_dimension_and_norm():
    text = "Product-Led Growth, freemium conversion, and PQL activation"
    vec = await get_text_embedding(text)
    assert len(vec) == 384
    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 1e-4

@pytest.mark.asyncio
async def test_retrieval_and_threshold_filtering():
    await init_db()
    async with async_session_factory() as session:
        # Insert a synthetic chunk for testing
        test_chunk_text = "[Episode: Growth Mastery | Guest: Elena Verna] Elena explains that Freemium is mandatory for collaborative tools."
        test_vec = await get_text_embedding(test_chunk_text)
        
        chunk = TranscriptChunkModel(
            episode_slug="test-slug",
            episode_title="Growth Mastery",
            guest_name="Elena Verna",
            timestamp_ref="00:10:00",
            chunk_index=0,
            chunk_text=test_chunk_text,
            token_count=100,
            embedding=test_vec
        )
        session.add(chunk)
        await session.commit()

        retriever = TranscriptRetriever(session)
        # 1. Query with high semantic overlap
        relevant_chunks = await retriever.retrieve_relevant_chunks(
            query="What does Elena say about freemium for collaborative tools?",
            top_k=3,
            similarity_threshold=0.30
        )
        assert len(relevant_chunks) > 0
        assert relevant_chunks[0]["guest"] == "Elena Verna"

        # 2. Out-of-domain query with strict threshold
        unrelated_chunks = await retriever.retrieve_relevant_chunks(
            query="Quantum mechanics black hole astrophysics",
            top_k=3,
            similarity_threshold=0.85
        )
        assert len(unrelated_chunks) == 0
