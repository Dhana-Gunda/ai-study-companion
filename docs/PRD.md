# Product Requirements Document (PRD)
## The Lenny Growth Assistant (Forward Deployed Engineer Assignment)

**Document Version:** 1.0  
**Author:** Forward Deployed Engineer  
**Status:** Approved for Implementation  

---

## 1. Discovery Brief & Problem Statement

### 1.1 The User & The Pain
- **Target Persona:** Growth Leaders, Product Managers, Founders, and Product Operations teams.
- **The Core Problem:** *Lenny's Podcast* is the definitive repository of modern tech wisdom, spanning over 200 episodes and 500+ hours of conversations with world-class operators (e.g., Shreyas Doshi, Elena Verna, Brian Chesky, Gustaf Alströmer). However:
  1. **Knowledge is Trapped:** Finding specific operational frameworks (e.g., B2B PLG loops, LNO prioritization, marketplace cold-starts) requires scrubbing through hours of audio or guessing keywords in raw search engines.
  2. **Generic LLM Hallucinations:** Asking general-purpose chatbots yields generic advice without verifiable attribution to actual episode transcripts or the specific practitioner who coined the tactic.
  3. **Output Friction:** Turning an insight into actionable work products (e.g., an executive summary, team memo, or an interactive ROI calculator) requires manual prompt engineering.

### 1.2 The Solution: "The Lenny Growth Assistant"
A full-stack, enterprise-grade, retrieval-augmented conversational assistant that:
1. Answers product/growth inquiries strictly grounded in verified podcast transcripts with direct episode and timestamp attribution.
2. Formats insights into ready-to-share assets using a dedicated **Ship 30 for 30** content engine (~1,250 words, 1-3-1 rhythm, skimmable anchors).
3. Renders native interactive artifacts (Markdown briefs, complete HTML/CSS components) beside the chat in a sandboxed, Claude-style Artifact Viewer.
4. Provides dual-engine execution: a local LLM via Ollama (mandatory for zero-cost private demo evaluation) and a cloud LLM toggle (Anthropic Claude 3.5 / OpenAI GPT-4o) with zero code changes.

---

## 2. Measurable Success Metrics

| Category | Metric | Target | Rationale |
|---|---|---|---|
| **Retrieval Accuracy** | Grounded Citation Rate | $\ge 95\%$ | Factual claims must map to verified transcript chunks with guest name & timestamp. |
| **Hallucination Control** | Out-of-Domain Graceful Rejection | $100\%$ | If query cannot be answered from Lenny's corpus, the assistant explicitly states context absence. |
| **Performance** | Local Inference Latency (Ollama) | $< 3.5\text{s}$ to first token | Smooth streaming experience on standard local machines (e.g., 4-core CPU / 16GB RAM). |
| **Content Quality** | Ship 30 for 30 Structure Fidelity | $100\%$ compliance | Generates ~1,250 words, 1-3-1 cadence, bold bullet anchors, and clear tactical takeaway. |
| **Security** | Artifact Isolation Safety | $0$ XSS / DOM Leaks | Sandboxed iframe (`sandbox="allow-scripts"` without `allow-same-origin`) prevents storage/cookie exfiltration. |
| **Operability** | Evaluator Time-to-Run | $< 5$ minutes | One command (`docker-compose up` or local run script) launches full stack with zero config blockers. |

---

## 3. Assumptions & Scope

### 3.1 Key Assumptions
1. **Model Availability:** Evaluators will run a local Ollama instance (e.g. `llama3.2:3b`, `llama3.1:8b`, or `mistral:7b`) on `localhost:11434`, or supply an optional `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`.
2. **Transcript Corpus:** Transcripts are sourced from the public repository (`github.com/ChatPRD/lennys-podcast-transcripts`). High-impact seed transcripts are pre-bundled in the repository to guarantee instant out-of-the-box operation even if internet access is restricted.
3. **Database Environment:** Production/Docker setup runs PostgreSQL with the `pgvector` extension; a local SQLite hybrid vector fallback is embedded to allow instantaneous local development without requiring Docker daemon.

### 3.2 In-Scope vs. Out-of-Scope

#### In-Scope (P0 / P1)
- [x] Context-aware transcript ingestion, speaker identification, and recursive chunking ($500\text{--}800$ tokens with $100$-token overlap).
- [x] Vector embedding generation and cosine similarity search ($K=5$ chunks, similarity threshold $\ge 0.60$).
- [x] Dynamic LLM switching between local Ollama and Cloud Claude/OpenAI via UI toggle and API headers.
- [x] Server-Sent Events (SSE) token streaming for real-time responsiveness.
- [x] Dedicated Ship 30 for 30 essay generation skill with custom prompt engineering and length constraints.
- [x] Side-by-side Claude-style Artifact Viewer rendering Markdown and sandboxed HTML/CSS widgets.
- [x] Persistent chat sessions, message history, and metadata stored in database.
- [x] Docker Compose multi-service deployment (`db`, `backend`, `frontend`).
- [x] Comprehensive test suite (unit, integration, retrieval evaluation).

#### Out-of-Scope (Future Iterations)
- [ ] Live audio transcription pipeline from YouTube/Spotify RSS feeds (use pre-generated transcripts instead).
- [ ] Multi-tenant enterprise SSO (SAML/Okta) and RBAC permissions.
- [ ] Multi-agent debate loops (single orchestrator with specialized skills is optimal for latency).

---

## 4. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy |
|---|---|---|---|
| **Local LLM Hallucination** | High | Medium | Strict system prompt rules; high retrieval similarity threshold ($\ge 0.60$); fallback response triggers when retrieved context is empty. |
| **Untrusted HTML in Artifacts (XSS)** | Critical | Low | Render HTML only in an `<iframe>` with `sandbox="allow-scripts"` and strictly omit `allow-same-origin`; pre-sanitize using DOMPurify. |
| **Local Model Latency & Timeouts** | Medium | Medium | Token-by-token SSE streaming provides immediate visual feedback; default to quantized lightweight models (`llama3.2:3b` or `qwen2.5:3b`). |
| **PostgreSQL / Docker Unavailable on Evaluator Machine** | High | Low | Intelligent automatic fallback to async SQLite with local vector similarity scoring if Postgres connection fails. |
| **API Key Missing for Cloud Models** | Low | Medium | UI displays clear status badges; defaults to Ollama if cloud key is not set; returns helpful error toast. |

---

## 5. Acceptance Criteria

1. **Grounded Question Answering:** Given a prompt like *"What does Elena Verna say about B2B Product-Led Growth and freemium retention?"*, the system streams a response citing Elena Verna's episode and specific concepts (e.g., self-serve funnels, product-led sales handoff).
2. **Out-of-Domain Guardrail:** Given a query unrelated to the corpus (e.g., *"How do I bake sourdough bread?"*), the assistant politely states that Lenny's podcast archive contains no relevant material on the topic.
3. **Ship 30 for 30 Generation:** Triggering the Ship 30 for 30 skill produces a long-form essay (~1,250 words) featuring a hook, 1-3-1 cadence, bold bullet anchors, and grounded takeaways.
4. **Artifact Rendering:** When requested to generate an interactive ROI calculator or formatted growth brief, an artifact is automatically detected and rendered side-by-side in the Artifact Viewer.
5. **Model Toggle:** The evaluator can switch between Ollama and Claude in the top navbar; subsequent requests stream through the chosen provider without restarting the server.
