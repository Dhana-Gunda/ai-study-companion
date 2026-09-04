import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator

from app.database import get_db
from app.models.db_models import SessionModel, MessageModel, ArtifactModel
from app.models.schemas import ChatRequest
from app.rag.retriever import TranscriptRetriever
from app.providers import get_llm_provider
from app.skills.ship30_writer import build_ship30_prompt
from app.skills.artifact_generator import artifact_extractor, ARTIFACT_SYSTEM_INSTRUCTION
from app.config import settings

logger = logging.getLogger("lenny_assistant.api.chat")

router = APIRouter(prefix="/chat", tags=["Chat"])

DEFAULT_GROUNDED_SYSTEM_PROMPT = """
You are "The Lenny Growth Assistant", a specialized AI copilot for product managers, founders, and growth leaders.
Your knowledge comes strictly from verified transcripts of Lenny's Podcast.

### Instructions:
1. **Grounding & Attribution:** Answer the user's question using ONLY the provided transcript context. Always cite the guest and episode when stating tactics or metrics, using inline citations like `[Guest Name, Episode: Title, Timestamp]`.
2. **Missing Information Guardrail:** If the provided context does NOT contain the answer, or if the context is empty, you MUST state clearly:
   "I do not have sufficient information in Lenny's podcast archive to answer this question."
   Do NOT make up facts or use external knowledge without explicitly disclaiming it.
3. **Tone & Style:** Practical, tactical, concise, and structured. Use Markdown lists and bold text for clarity.
4. **Artifact Generation:** If the user asks for a self-contained guide, table, template, or interactive HTML tool, enclose it in `<artifact type="markdown|html" title="...">...</artifact>` tags.

Context from Lenny's Podcast Transcripts:
{context_data}
"""

@router.post("")
async def stream_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Stream conversation tokens with grounded citations and artifact extraction."""
    # 1. Verify or create session
    stmt = select(SessionModel).where(SessionModel.id == req.session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        session = SessionModel(id=req.session_id, title=req.message[:50] + "...")
        db.add(session)
        await db.commit()

    # 2. Save user message to database
    user_msg = MessageModel(
        session_id=session.id,
        role="user",
        content=req.message,
        provider=req.provider or settings.DEFAULT_PROVIDER,
        model=req.model or "default"
    )
    db.add(user_msg)
    await db.commit()

    # 3. Retrieve relevant transcript chunks
    retriever = TranscriptRetriever(db)
    retrieved_chunks = await retriever.retrieve_relevant_chunks(
        query=req.message,
        top_k=settings.RETRIEVAL_TOP_K,
        similarity_threshold=settings.SIMILARITY_THRESHOLD
    )

    # 4. Prepare System Prompt based on Mode
    if req.mode == "ship30":
        system_prompt = build_ship30_prompt(req.message, retrieved_chunks)
    else:
        if retrieved_chunks:
            context_text = "\n\n".join([
                f"--- [Episode: {c['episode']} | Guest: {c['guest']} | Ref: {c['timestamp']}] ---\n{c['text']}"
                for c in retrieved_chunks
            ])
        else:
            context_text = "NO RELEVANT PODCAST TRANSCRIPTS FOUND FOR THIS QUERY."

        system_prompt = DEFAULT_GROUNDED_SYSTEM_PROMPT.format(context_data=context_text)
        if req.mode == "artifact":
            system_prompt += f"\n\n{ARTIFACT_SYSTEM_INSTRUCTION}"

    # 5. Fetch previous conversation messages for conversational memory
    msg_stmt = (
        select(MessageModel)
        .where(MessageModel.session_id == session.id)
        .order_by(MessageModel.created_at)
    )
    msg_res = await db.execute(msg_stmt)
    history = msg_res.scalars().all()
    # Format last 6 messages
    recent_messages = []
    for m in history[-6:]:
        recent_messages.append({"role": m.role, "content": m.content})

    # 6. Instantiate dynamic LLM Provider
    provider = get_llm_provider(provider_name=req.provider, model_name=req.model)

    # 7. SSE Streaming Generator
    async def sse_event_stream() -> AsyncGenerator[str, None]:
        full_response_text = ""

        # Step A: Emit Status Event
        yield f"data: {json.dumps({'type': 'status', 'content': 'Searching Lenny transcripts...'})}\n\n"

        # Step B: Emit Grounded Citations
        citations_payload = [
            {
                "episode": c["episode"],
                "guest": c["guest"],
                "timestamp": c["timestamp"],
                "score": c["score"]
            }
            for c in retrieved_chunks
        ]
        yield f"data: {json.dumps({'type': 'citations', 'citations': citations_payload})}\n\n"

        # Step C: Stream Tokens
        try:
            async for token in provider.generate_response(
                messages=recent_messages,
                system_prompt=system_prompt
            ):
                full_response_text += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as gen_err:
            logger.error(f"Error during provider streaming: {gen_err}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(gen_err)})}\n\n"

        # Step D: Detect and Extract Artifact if present
        detected_artifact = artifact_extractor.extract_artifact(full_response_text)
        if detected_artifact:
            yield f"data: {json.dumps({'type': 'artifact', 'artifact': detected_artifact})}\n\n"

        # Step E: Persist Assistant Message and Artifact in Database
        try:
            # We open a dedicated session for background saving to avoid conflicts
            assistant_msg = MessageModel(
                session_id=session.id,
                role="assistant",
                content=full_response_text,
                sources=citations_payload,
                provider=req.provider or settings.DEFAULT_PROVIDER,
                model=getattr(provider, "model", "default")
            )
            db.add(assistant_msg)
            await db.commit()
            await db.refresh(assistant_msg)

            if detected_artifact:
                artifact_entry = ArtifactModel(
                    message_id=assistant_msg.id,
                    title=detected_artifact["title"],
                    artifact_type=detected_artifact["artifact_type"],
                    content=detected_artifact["content"]
                )
                db.add(artifact_entry)
                await db.commit()
        except Exception as db_save_err:
            logger.error(f"Failed to persist assistant message: {db_save_err}")

        # Step F: Emit Done
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
