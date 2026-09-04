"""
Knowledge Base Ingestion Script for The Lenny Growth Assistant.
Parses transcripts, generates embeddings, and populates the database vector index.
"""
import os
import sys
import re
import asyncio
from pathlib import Path

# Add backend directory to PYTHONPATH
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

from app.database import async_session_factory, init_db, engine
from app.models.db_models import TranscriptChunkModel
from app.rag.chunker import chunker
from app.rag.embeddings import get_text_embedding
from sqlalchemy import delete

TRANSCRIPTS_DIR = BACKEND_DIR / "data" / "transcripts"

def parse_transcript_metadata(content: str, filename: str):
    """Extract episode title, guest name, and slug from transcript front matter."""
    lines = content.splitlines()
    title = ""
    guest = "Unknown Guest"
    
    # Try to find # Title
    for line in lines:
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break

    # Look for Guest: ...
    guest_match = re.search(r'\*\*Guest:\*\*\s*([^\n]+)', content)
    if guest_match:
        guest = guest_match.group(1).strip()
        # Clean up any parentheses
        guest = re.sub(r'\(.*?\)', '', guest).strip()

    if not title:
        title = filename.replace(".md", "").replace("-", " ").title()

    slug = filename.replace(".md", "")
    return title, guest, slug

async def ingest_all_transcripts():
    print("=" * 60)
    print(" The Lenny Growth Assistant - Transcript Ingestion Pipeline")
    print("=" * 60)

    # Initialize DB tables
    await init_db()

    if not TRANSCRIPTS_DIR.exists():
        print(f"[!] Transcripts directory not found: {TRANSCRIPTS_DIR}")
        return

    transcript_files = list(TRANSCRIPTS_DIR.glob("*.md")) + list(TRANSCRIPTS_DIR.glob("*.txt"))
    if not transcript_files:
        print("[!] No transcript files found to ingest.")
        return

    print(f"[*] Found {len(transcript_files)} transcript file(s) for indexing.\n")

    total_chunks_indexed = 0

    async with async_session_factory() as session:
        # Clear existing transcript chunks for clean re-indexing
        print("[*] Clearing prior index...")
        await session.execute(delete(TranscriptChunkModel))
        await session.commit()

        for file_path in transcript_files:
            print(f"[*] Processing: {file_path.name}")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            title, guest, slug = parse_transcript_metadata(content, file_path.name)
            print(f"    - Title: {title}")
            print(f"    - Guest: {guest}")

            # Dialogue-aware chunking
            chunks = chunker.chunk_transcript(
                text=content,
                episode_title=title,
                guest_name=guest,
                episode_slug=slug
            )
            print(f"    - Generated {len(chunks)} contextual chunks.")

            # Compute embeddings and insert
            for c in chunks:
                vec = await get_text_embedding(c["chunk_text"])
                db_chunk = TranscriptChunkModel(
                    episode_slug=c["episode_slug"],
                    episode_title=c["episode_title"],
                    guest_name=c["guest_name"],
                    timestamp_ref=c["timestamp_ref"],
                    chunk_index=c["chunk_index"],
                    chunk_text=c["chunk_text"],
                    token_count=c["token_count"],
                    embedding=vec
                )
                session.add(db_chunk)
                total_chunks_indexed += 1

            await session.commit()
            print(f"    [✓] Ingested {len(chunks)} chunks into vector store.\n")

    print("=" * 60)
    print(f"[✓] Ingestion complete! Total chunks indexed: {total_chunks_indexed}")
    print(f"[✓] Storage Engine: {engine.url}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(ingest_all_transcripts())
