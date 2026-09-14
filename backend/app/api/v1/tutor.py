import json
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, async_session_maker
from app.models.db_models import (
    Project, Conversation, Message, LearningContext, AIRequestLog, LearningEvent
)
from app.api.v1.deps import verify_project_ownership, get_current_user
from app.modules.knowledge.retriever import KnowledgeRetriever
from app.modules.ai.client import get_llm_client
from app.modules.ai.context import ContextComposer
from app.modules.ai.guardrails import EvidenceGuardrail
from app.modules.ai.prompts import PromptTemplates

router = APIRouter(tags=["AI Tutor"])

class TutorChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    tokens_used: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    project_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

@router.get("/projects/{project_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    project_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """List all study conversations within a project."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project.id)
        .order_by(Conversation.updated_at.desc())
    )
    convs = result.scalars().all()
    output = []
    for c in convs:
        output.append(
            ConversationResponse(
                id=c.id,
                project_id=c.project_id,
                title=c.title or "Study Session",
                created_at=c.created_at,
                updated_at=c.updated_at,
                messages=[]
            )
        )
    return output

@router.get("/projects/{project_id}/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    project_id: str,
    conversation_id: str,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Get conversation history with all messages and citations."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id, Conversation.project_id == project.id
        )
    )
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    msg_res = await db.execute(
        select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at.asc())
    )
    messages = [MessageResponse.model_validate(m) for m in msg_res.scalars().all()]

    return ConversationResponse(
        id=conv.id,
        project_id=conv.project_id,
        title=conv.title or "Study Session",
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=messages
    )

@router.post("/projects/{project_id}/tutor/chat")
async def tutor_chat_stream(
    project_id: str,
    req: TutorChatRequest,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Grounded AI Tutor chat with citations, prompt-injection defense, and low-evidence refusal via SSE streaming."""
    start_time = time.time()
    user_query = req.message.strip()

    # 1. Fetch or create Conversation
    conversation_id = req.conversation_id
    if conversation_id:
        c_res = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id, Conversation.project_id == project.id)
        )
        conv = c_res.scalars().first()
    else:
        conv = None

    if not conv:
        title_snippet = (user_query[:35] + "...") if len(user_query) > 35 else user_query
        conv = Conversation(
            project_id=project.id,
            user_id=project.user_id,
            title=title_snippet
        )
        db.add(conv)
        await db.flush()

    # 2. Fetch past conversation history
    history_res = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at.desc())
        .limit(6)
    )
    past_messages = list(reversed(history_res.scalars().all()))
    history_dicts = [{"role": m.role, "content": m.content} for m in past_messages]

    # 3. Fetch persistent LearningContext
    lc_res = await db.execute(select(LearningContext).where(LearningContext.project_id == project.id))
    lc = lc_res.scalars().first()
    lc_payload = lc.state_payload if lc else {}

    # 4. Generate query embedding and retrieve evidence from pgvector
    llm = get_llm_client()
    query_vectors = await llm.get_embeddings([user_query])
    query_vector = query_vectors[0] if query_vectors else []

    retriever = KnowledgeRetriever(db)
    evidence = await retriever.retrieve(
        project_id=project.id,
        query_vector=query_vector,
        top_k=4,
        threshold=0.60
    )

    # 5. Check Low-Evidence Guardrail
    has_evidence = EvidenceGuardrail.has_sufficient_evidence(evidence, min_chunks=1)

    # Save user message to database
    user_msg_record = Message(
        conversation_id=conv.id,
        role="user",
        content=user_query,
        tokens_used=len(user_query.split())
    )
    db.add(user_msg_record)
    await db.commit()

    async def event_generator():
        accumulated_text = ""
        conv_id = conv.id

        if not has_evidence:
            # Low-evidence refusal branch
            refusal_text = EvidenceGuardrail.generate_insufficient_evidence_refusal()
            yield f"data: {json.dumps({'token': refusal_text, 'type': 'token'})}\n\n"
            accumulated_text = refusal_text

            latency = (time.time() - start_time) * 1000.0
            # Persist assistant response and AIRequestLog in a fresh session
            async with async_session_maker() as session:
                assistant_msg = Message(
                    conversation_id=conv_id,
                    role="assistant",
                    content=accumulated_text,
                    sources=[],
                    tokens_used=len(accumulated_text.split())
                )
                session.add(assistant_msg)

                log_entry = AIRequestLog(
                    user_id=project.user_id,
                    project_id=project.id,
                    feature="tutor_chat",
                    provider="openai",
                    model="gpt-4o-mini",
                    prompt_tokens=len(user_query.split()),
                    completion_tokens=len(accumulated_text.split()),
                    latency_ms=round(latency, 2),
                    cost_usd=0.0001,
                    status="REFUSED_LOW_EVIDENCE",
                    error_message="Insufficient project material evidence found above threshold."
                )
                session.add(log_entry)
                await session.commit()

            yield f"data: {json.dumps({'done': True, 'conversation_id': conv_id, 'citations': [], 'refused': True})}\n\n"
            return

        # Grounded Tutor stream branch
        system_prompt = PromptTemplates.TUTOR_SYSTEM_PROMPT
        composed_prompt = ContextComposer.compose_tutor_prompt(
            user_message=user_query,
            evidence=evidence,
            learning_context=lc_payload,
            recent_history=history_dicts
        )

        stream = llm.generate_stream(prompt=composed_prompt, system_prompt=system_prompt)
        async for chunk in stream:
            accumulated_text += chunk
            yield f"data: {json.dumps({'token': chunk, 'type': 'token'})}\n\n"

        citations = [
            {
                "chunk_id": e.get("chunk_id"),
                "filename": e.get("filename"),
                "page_number": e.get("page_number"),
                "similarity": e.get("similarity")
            }
            for e in evidence
        ]

        latency = (time.time() - start_time) * 1000.0

        # Persist assistant response, log and event in fresh session
        async with async_session_maker() as session:
            assistant_msg = Message(
                conversation_id=conv_id,
                role="assistant",
                content=accumulated_text,
                sources=citations,
                tokens_used=len(accumulated_text.split())
            )
            session.add(assistant_msg)

            log_entry = AIRequestLog(
                user_id=project.user_id,
                project_id=project.id,
                feature="tutor_chat",
                provider="openai",
                model="gpt-4o-mini",
                prompt_tokens=len(composed_prompt.split()),
                completion_tokens=len(accumulated_text.split()),
                latency_ms=round(latency, 2),
                cost_usd=0.0003,
                status="SUCCESS"
            )
            session.add(log_entry)

            event = LearningEvent(
                idempotency_key=f"tutor_chat_{conv_id}_{int(time.time()*1000)}",
                user_id=project.user_id,
                project_id=project.id,
                event_type="TUTOR_QUESTION_ASKED",
                payload={"conversation_id": conv_id, "query": user_query[:100], "citations_count": len(citations)}
            )
            session.add(event)
            await session.commit()

        yield f"data: {json.dumps({'done': True, 'conversation_id': conv_id, 'citations': citations, 'refused': False})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
