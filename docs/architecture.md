# System Architecture Specification: AI Study Companion

**System Name:** AI Study Companion  
**Architecture Pattern:** Clean Modular Hexagonal Architecture with Strict Tenant Isolation  
**Runtime:** Next.js 14 (Frontend) + FastAPI ASGI (Backend) + PostgreSQL 16 with pgvector + Redis  

---

## 1. High-Level Architecture Overview

The system is architected across decoupled layers ensuring zero leakage between learning projects, real-time citation tracking, and continuous mastery estimation:

```
                                  [ Client Browser ]
                     Next.js 14 (App Router, Tailwind, Shadcn/UI)
                                          │
                                          │ HTTP / SSE Token Stream
                                          ▼
                                 [ FastAPI Application ]
  ┌───────────────────────────────────────┼──────────────────────────────────────┐
  │                                       │                                      │
  ▼                                       ▼                                      ▼
[ Learning & Auth Module ]       [ AI & Retrieval Module ]         [ Assessment & Mastery ]
- JWT Bearer Auth                - Grounded RAG with Citations     - Adaptive Question Gen
- Space > Project Hierarchy      - Low-Evidence Refusal (<0.60)    - Open-Ended Rubric Eval
- Multi-Tenant Ownership Gates   - Prompt-Injection Boundaries     - EMA Mastery Tracking
  │                                       │                                      │
  └───────────────────────────────────────┼──────────────────────────────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
       [ PostgreSQL 16 + pgvector ]                     [ Redis In-Memory ]
       - 1536-dim Vector Embeddings                     - Job queues & locks
       - Zero-join Project Indexing                     - Pub/Sub events
       - Immutable Event Log                            - Fast caching
       - Strict Fail-Loud Requirement
```

---

## 2. Core Relational & Vector Schema

All project-scoped entities enforce a direct `project_id` foreign key index to guarantee query isolation without complex joins.

### Key Domain Models
1. **`User`**: `id`, `email`, `hashed_password` (bcrypt), `name`, `role` (`user`, `admin`).
2. **`Space`**: Top-level learning namespace (`user_id`, `name`, `description`).
3. **`Project`**: Core study boundary (`space_id`, `user_id`, `name`, `learning_goal`).
4. **`Material`**: Uploaded learning resource (`project_id`, `filename`, `file_path`, `status`, `page_count`).
5. **`DocumentChunk`**: Semantic text segment with 1536-dimensional vector embedding (`material_id`, `project_id`, `page_number`, `content`, `embedding Vector(1536)`).
6. **`Concept`**: Knowledge atom extracted from materials (`project_id`, `name`, `description`).
7. **`ConceptMastery`**: Real-time mastery state (`project_id`, `user_id`, `concept_id`, `mastery_score [0.0-1.0]`, `confidence_level`, `trend [IMPROVING|STABLE|ATTENTION]`).
8. **`MasterySnapshot`**: Historical timestamped mastery point for progress graphing.
9. **`Conversation` & `Message`**: Dialogue history with JSON citation provenance tags (`filename`, `page_number`, `similarity`).
10. **`QuizSession`, `Question`, `Answer`**: Diagnostic assessments with rubric evaluations.
11. **`LearningContext`**: Persistent learner summary (strengths, weak concepts, repeated mistakes).
12. **`LearningEvent`**: Immutable event stream with unique `idempotency_key`.
13. **`AIRequestLog`**: Telemetry capturing prompt tokens, completion tokens, latency, cost USD, and status (`SUCCESS`, `REFUSED_LOW_EVIDENCE`).
14. **`Recommendation`**: Actionable next step answering *"What should I do next?"*.

---

## 3. Grounded Retrieval & Guardrail Mechanics

1. **Embedding Generation**: User query embedded to 1536 dimensions.
2. **Project-Scoped Vector Search**:
   $$\text{similarity} = 1.0 - \text{cosine\_distance}(\mathbf{v}_{\text{query}}, \mathbf{v}_{\text{chunk}})$$
   filtered strictly by `project_id`.
3. **Low-Evidence Refusal Guardrail**:
   - If $\max(\text{similarity}) < 0.60$ or no chunks match:
     Refusal triggered: *"I do not have sufficient information in your uploaded project materials to answer this question reliably."*
   - Logged with `status="REFUSED_LOW_EVIDENCE"`.
4. **Provenance Citations**:
   - Injected into system prompt context with tags: `[Source: {filename} — Page {page_number}]`.
   - Rendered in frontend as interactive badge chips.

---

## 4. Adaptive Assessment & EMA Mastery Updates

- **Target Concept Selection**: Prioritizes concepts tagged as `ATTENTION` or score $< 0.50$ (60% weight).
- **Exponential Moving Average (EMA)** update formula:
  $$\text{Mastery}_{\text{new}} = 0.3 \cdot \text{Score}_{\text{new}} + 0.7 \cdot \text{Mastery}_{\text{prev}}$$
- **Trend Classification**:
  - $\Delta \ge +0.10 \implies \text{IMPROVING}$
  - $\text{Score} < 0.50 \text{ or } \Delta \le -0.10 \implies \text{ATTENTION}$
  - Otherwise $\implies \text{STABLE}$
