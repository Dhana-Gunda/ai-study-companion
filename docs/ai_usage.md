# AI Tools, Usage & Telemetry Documentation
## AI Study Companion (Candidate Challenge Edition — PRD Section 20 Compliance)

**Document Purpose:** Comprehensive specification clearly distinguishing:
1. **AI Used to Build the Product** (Development tools, agents, pair-programming assistants)
2. **AI Used by the Final Product** (Runtime models, RAG retrieval, guardrails, and telemetry)

---

## 1. AI Tools Used to Build the Product

| Tool / Technology | Role in Development Lifecycle | Key Contributions & Impact |
|---|---|---|
| **Google Antigravity AI Agent** | Primary AI Pair Programmer & System Architect | • Automated domain modeling across 16 SQLAlchemy async tables.<br>• Architected the modular hexagonal backend and fail-loud pgvector enforcement.<br>• Implemented Server-Sent Events (SSE) streaming and grounded citation pipeline.<br>• Wrote 19 automated pytest unit & integration tests.<br>• Automated cloud deployment orchestration across Neon, Render, and Vercel. |
| **Gemini 2.5 Coding Model** | Reasoning & Code Generation Engine | • Produced type-safe Next.js 14 frontend components (shadcn/ui, Tailwind).<br>• Solved cloud environment quirks (asyncpg URL normalization, CORS regex policies).<br>• Designed Exponential Moving Average (EMA) mathematical tracking formula for concept mastery. |
| **Playwright Automation Engine** | Automated Verification & Video Production | • Headless browser automation executing the 13-stage PRD learning loop.<br>• Recorded high-definition video walkthrough without manual friction. |

---

## 2. AI Used Inside the Final Runtime Product

```
                      [ User Query / Study Session ]
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                 Runtime AI Orchestration                │
       └────────────────────────────┬────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
[ Grounded AI Tutor ]     [ Adaptive Quiz Engine ]     [ Assessment & Rubrics ]
- gpt-4o-mini / Claude    - Dynamic Weak Concept       - Few-Shot Grading
- pgvector Cosine Search    Prioritization             - Concept Mastery Update
- Citation Provenance     - MCQ & Open-Ended Formats   - Growth Velocity (EMA)
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │             Guardrails & Telemetry Layer                │
       │  • Low-Evidence Refusal (<0.60 Cosine Threshold)        │
       │  • Prompt-Injection Strict Boundary Defense             │
       │  • Token Count, Latency, Cost USD Logging               │
       └─────────────────────────────────────────────────────────┘
```

### 2.1 Provider Abstraction & Model Selection
The runtime system leverages an abstracted `BaseLLMClient`:
- **Default Cloud LLM:** `gpt-4o-mini` (temperature 0.2, high throughput, cost-effective).
- **Secondary Cloud LLM:** `claude-3-5-sonnet-20241022` (for nuanced open-ended evaluations).
- **Embedding Model:** `text-embedding-3-small` (1536-dimensional normalized vectors).
- **Offline / Local Mock:** Deterministic vector and response generator ensuring instant, zero-cost automated test execution and headless CI/CD.

### 2.2 Grounded Retrieval-Augmented Generation (RAG)
- **Chunking:** Semantic sliding windows ($500\text{--}800$ tokens with $100$-token overlap) with page provenance (`page_number`, `filename`).
- **Vector Search:** Cosine similarity via PostgreSQL `pgvector` indexed on `project_id`.
- **Source Citations:** Every tutor response formats verifiable attribution badges: `[Source: {filename} — Page {page_number}]`.

### 2.3 Low-Evidence Refusal Guardrail
- **Trigger:** If the maximum cosine similarity among retrieved chunks is $< 0.60$, or if no documents exist in the active project.
- **Behavior:** The model halts speculation and emits a structured refusal:
  > *"I do not have sufficient information in your uploaded project materials to answer this question reliably. Please upload relevant notes or a PDF covering this topic."*
- **Audit:** Captured in `ai_request_logs` with `status = "REFUSED_LOW_EVIDENCE"`.

### 2.4 Prompt-Injection Defense
System instructions and untrusted document chunks are strictly segregated into distinct prompt sections with immutable system boundary markers. Adversarial inputs inside user PDF chunks cannot override tutor behavior.

### 2.5 Concept Mastery (EMA) & Growth Engine
- Mastery is updated after every assessment event using Exponential Moving Average:
  $$\mathcal{M}_t = \alpha \cdot s_t + (1 - \alpha) \cdot \mathcal{M}_{t-1}, \quad \text{where } \alpha = 0.3$$
- **Trend Detection:**
  - $\Delta > +0.05 \implies$ `IMPROVING`
  - $\Delta < -0.05 \text{ or } \mathcal{M}_t < 0.50 \implies$ `ATTENTION`
  - Otherwise $\implies$ `STABLE`

---

## 3. Observability & AI Spend Telemetry

Every AI request records a structured record in the `ai_request_logs` table:
- `feature`: `tutor_chat`, `quiz_generator`, `rubric_evaluator`.
- `provider`: `openai`, `anthropic`, or `local`.
- `model`: e.g. `gpt-4o-mini`.
- `prompt_tokens` & `completion_tokens`.
- `latency_ms`: total execution duration.
- `cost_usd`: calculated dynamically from provider token rate cards.
- `status`: `SUCCESS`, `ERROR`, `REFUSED_LOW_EVIDENCE`.

Administrators can inspect live aggregated AI metrics at `GET /api/v1/admin/ai-metrics` and via the Admin Dashboard UI.
