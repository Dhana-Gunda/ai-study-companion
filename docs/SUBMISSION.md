# Candidate Challenge Submission: AI Study Companion
> **Role:** Full Stack AI Engineer Candidate  
> **Repository:** [https://github.com/Dhana-Gunda/ai-study-companion](https://github.com/Dhana-Gunda/ai-study-companion)  
> **Target:** 3 - 4 Day Prototype Submission (PRD Section 20)

---

## 1. Working Application Links

- **Live Production Frontend (Vercel):**  
  👉 [https://ai-study-companion-gamma.vercel.app/](https://ai-study-companion-gamma.vercel.app/)
- **Live Production Backend API (Render):**  
  👉 [https://ai-study-companion-backend-azlw.onrender.com/](https://ai-study-companion-backend-azlw.onrender.com/)
- **Interactive OpenAPI Swagger Docs:**  
  👉 [https://ai-study-companion-backend-azlw.onrender.com/docs](https://ai-study-companion-backend-azlw.onrender.com/docs)
- **Deep Health Check & Connectivity Probe:**  
  👉 [https://ai-study-companion-backend-azlw.onrender.com/api/v1/health](https://ai-study-companion-backend-azlw.onrender.com/api/v1/health)  
  *(Returns HTTP 200 OK, latency ~12ms, database `connected` with `pgvector_enabled: true` on Neon.tech PostgreSQL 16).*

---

## 2. Demo Video (PRD Section 20 Core Learning Loop Walkthrough)

- **Interactive Video Player Page:**  
  👉 [https://ai-study-companion-gamma.vercel.app/demo](https://ai-study-companion-gamma.vercel.app/demo)
- **Direct Video Stream (WebM / HD):**  
  👉 [https://ai-study-companion-gamma.vercel.app/demo_video.webm](https://ai-study-companion-gamma.vercel.app/demo_video.webm)
- **Walkthrough Chapters & Script:** Defined in detail in [`demo_script.md`](../demo_script.md):
  1. *Stack Probe* (All Services Connected)
  2. *Create Space* (Domain namespace)
  3. *Create Project* (Goal definition)
  4. *Upload Material* (PDF ingestion)
  5. *Process Material* (PyMuPDF chunking & pgvector indexing)
  6. *Ask Tutor* (SSE streaming chat)
  7. *Grounded Answer + Citations* (Page provenance)
  8. *Unsupported Question Handling* (Refusal guardrail)
  9. *Adaptive Quiz* (Targeted weak concepts)
  10. *Open-Ended Assessment* (Rubric evaluation)
  11. *Mastery & Growth* (EMA concept score & trend)
  12. *Recommendation* (Targeted next learning action)
  13. *Admin Dashboard* (Observability & token telemetry)

---

## 3. Public GitHub Repository

- **URL:** [https://github.com/Dhana-Gunda/ai-study-companion](https://github.com/Dhana-Gunda/ai-study-companion)
- Contains complete source code:
  - `backend/`: FastAPI application, modular domain layers, SQLAlchemy async models, PyMuPDF chunking, pgvector similarity search, adaptive quiz engine, EMA mastery calculators, and 19 automated pytest tests.
  - `frontend/`: Next.js 14 App Router, Tailwind CSS, shadcn/ui components, real-time SSE streaming tutor, interactive quiz runner, and live connectivity probe.
  - `docs/`: Architecture specification, deployment guide, AI usage telemetry, and candidate evaluation documentation.

---

## 4. Architecture Documentation

- **Full Architecture Spec:** See [`docs/architecture.md`](./architecture.md).
- **Core Design Decisions:**
  1. **Strict Tenant & Project Isolation:** Every domain entity enforces a direct `project_id` foreign key. Cross-tenant access is rejected at the dependency layer with HTTP 403.
  2. **Fail-Loud PostgreSQL + pgvector:** No silent SQLite fallbacks in production. Database requires PostgreSQL with pgvector for 1536-dimensional semantic search.
  3. **Event-Driven Learning Loop:** An immutable learning event stream (`learning_events`) ensures idempotency and drives historical growth analytics.
  4. **Exponential Moving Average (EMA) Mastery:** Mastery score $\mathcal{M}_t = \alpha \cdot s_t + (1 - \alpha) \cdot \mathcal{M}_{t-1}$ tracks understanding velocity and assigns growth trends (`IMPROVING`, `STABLE`, `ATTENTION`).

---

## 5. AI Usage Documentation

- **Full AI Usage Guide:** See [`docs/ai_usage.md`](./ai_usage.md).
- **AI Used to Build the Product:**
  - *Antigravity AI Agent:* Full-stack scaffolding, PostgreSQL migration setup, seed data generators, test writing, and cloud deployment orchestration.
- **AI Used by the Final Product:**
  - *Grounded AI Tutor:* RAG grounded in uploaded PDF chunks with strict page citations (`[Source: {filename} — Page {p}]`).
  - *Low-Evidence Refusal Guardrail:* Rejects queries when chunk similarity $< 0.60$ instead of hallucinating.
  - *Adaptive Quiz Generator & Evaluator:* Formulates targeted questions on weak concepts and grades open-ended responses against rubrics.
  - *Provider Abstraction:* Unified client supporting OpenAI (`gpt-4o-mini`), Anthropic (`claude-3-5-sonnet`), and offline deterministic mock for headless testing.

---

## 6. Development Prompts Used

The prompts used during development are structured across categories in [`agent_transcripts/prompts.md`](../agent_transcripts/prompts.md):
- **Architecture:** Decoupled modular design, Space > Project boundary definition, and fail-loud pgvector enforcement.
- **Backend & Database:** Async SQLAlchemy schema creation, vector chunking with provenance, and ownership guard middleware.
- **AI & Guardrails:** Prompt injection boundaries, evidence threshold checking, and structured SSE token streaming.
- **Frontend & UI:** Dark-mode dashboard, interactive quiz runner, and live connectivity probe.
- **DevOps & Cloud:** Neon PostgreSQL connection pooling, Render deployment, and Vercel build configuration.

---

## 7. Evaluation Approach

- **Automated Tests:** 19/19 pytest tests passing across auth isolation, grounding guardrails, prompt injection defenses, adaptive concept selection, and EMA calculations.
- **Grounded Citation Accuracy:** Asserts presence of `filename` and `page_number` in every tutor response.
- **Refusal Verification:** Out-of-domain prompts (e.g. baking bread) reliably trigger structured refusal without hallucination.
- **Admin Observability:** Real-time logging of prompt tokens, completion tokens, execution latency, and cost USD per request.

---

## 8. Known Limitations

1. **Scanned PDF OCR:** PyMuPDF handles digital and vector PDFs; scanned handwritten notes require an external OCR pipeline (e.g., Tesseract or AWS Textract).
2. **Cloud Free-Tier Cold Starts:** Render free tier spins down on idle; first wake-up request takes ~40 seconds.
3. **Queue Scalability:** Standalone in-memory fallback enabled for serverless deployment; production horizontal scaling requires dedicated Redis cluster.

---

## 9. Future Improvements

1. **Interactive Concept Maps:** Force-directed visual graph of prerequisite relationships between concepts.
2. **Multi-Modal Diagrams:** Rendering mathematical equations and extracted textbook figures inline within tutor chat.
3. **Collaborative Study Spaces:** Multi-user shared projects with peer discussion and group quiz leaderboards.
