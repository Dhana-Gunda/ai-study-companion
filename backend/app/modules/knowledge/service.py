import os
import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.db_models import Material, DocumentChunk, Concept, LearningEvent
from app.modules.knowledge.parser import DocumentParser
from app.modules.knowledge.chunker import DocumentChunker
from app.modules.ai.client import get_llm_client

logger = logging.getLogger("material_service")

class MaterialIngestionService:
    @staticmethod
    async def process_material(material_id: str, db: AsyncSession) -> bool:
        """Processes an uploaded PDF material: parsing, chunking, embedding generation, and concept extraction."""
        result = await db.execute(select(Material).where(Material.id == material_id))
        material = result.scalars().first()
        if not material:
            logger.error(f"Material {material_id} not found for processing.")
            return False

        material.status = "PROCESSING"
        material.error_message = None
        await db.commit()

        try:
            if not os.path.exists(material.file_path):
                raise FileNotFoundError(f"File not found on disk: {material.file_path}")

            # 1. Parse PDF pages
            pages = DocumentParser.parse_pdf(material.file_path)
            if not pages:
                raise ValueError("PDF contained no extractable text.")

            material.page_count = len(pages)

            # 2. Chunk pages into semantic windows with provenance
            chunker = DocumentChunker(chunk_size=350, chunk_overlap=40)
            chunks_data = chunker.chunk_pages(pages)

            if not chunks_data:
                raise ValueError("No text chunks could be produced from document.")

            # 3. Generate embeddings
            texts = [c["content"] for c in chunks_data]
            llm_client = get_llm_client()
            embeddings = await llm_client.get_embeddings(texts)

            # 4. Idempotent cleanup of any previous chunks for this material
            await db.execute(delete(DocumentChunk).where(DocumentChunk.material_id == material.id))

            # 5. Insert DocumentChunk records
            for i, cdata in enumerate(chunks_data):
                chunk = DocumentChunk(
                    material_id=material.id,
                    project_id=material.project_id,
                    chunk_index=cdata["chunk_index"],
                    page_number=cdata["page_number"],
                    content=cdata["content"],
                    token_count=cdata["token_count"],
                    embedding=embeddings[i] if i < len(embeddings) else None
                )
                db.add(chunk)

            # 6. Extract key concepts if project lacks concepts
            c_res = await db.execute(select(Concept).where(Concept.project_id == material.project_id))
            existing_concepts = c_res.scalars().all()
            if len(existing_concepts) < 2:
                # Add initial default concepts extracted from filename/text
                sample_name = material.filename.replace(".pdf", "").replace("_", " ").title()
                new_concept = Concept(
                    project_id=material.project_id,
                    name=sample_name,
                    description=f"Core subject domain extracted from {material.filename}"
                )
                db.add(new_concept)

            # 7. Record LearningEvent
            event = LearningEvent(
                idempotency_key=f"material_ingested_{material.id}_{len(chunks_data)}",
                user_id="system",
                project_id=material.project_id,
                event_type="MATERIAL_INDEXED",
                payload={
                    "material_id": material.id,
                    "filename": material.filename,
                    "page_count": len(pages),
                    "chunk_count": len(chunks_data)
                }
            )
            db.add(event)

            material.status = "READY"
            material.error_message = None
            await db.commit()
            logger.info(f"Successfully processed material {material.filename} ({len(chunks_data)} chunks).")
            return True

        except Exception as e:
            logger.error(f"Failed to process material {material_id}: {e}", exc_info=True)
            material.status = "FAILED"
            material.error_message = str(e)
            await db.commit()
            return False
