# AI Usage, Telemetry & Guardrail Guide

**Document Purpose:** Architectural guide for LLM interactions, token economics, latency monitoring, and safety guardrails.

---

## 1. Provider Abstraction & Model Selection

The application abstracts LLM providers via `BaseLLMClient`:
- **Default Cloud Model:** `gpt-4o-mini` (temperature 0.2, fast response, low cost).
- **Secondary Cloud Model:** `claude-3-5-sonnet-20241022` (for complex open-ended evaluations).
- **Embedding Model:** `text-embedding-3-small` (1536 dimensions, normalized unit vectors).
- **Offline / Local Mock:** Deterministic vector and text generator for headless testing without incurring API charges.

---

## 2. Guardrails & Safety Protocols

### Low-Evidence Refusal Guardrail
- **Trigger**: When maximum cosine similarity of retrieved document chunks is below $0.60$ or when no documents have been uploaded to the active project.
- **Behavior**: The model halts speculation and streams a polite refusal:
  > *"I do not have sufficient information in your uploaded project materials to answer this question reliably. Please upload relevant notes or a PDF covering this topic."*
- **Telemetry**: Logged to `ai_request_logs` with `status = "REFUSED_LOW_EVIDENCE"`.

### Prompt-Injection Defense
- System instructions are strictly segregated from untrusted user documents and query inputs:
  ```markdown
  ### SYSTEM INSTRUCTIONS & CITATION RULES
  [Hardcoded constraints]

  ### RETRIEVED PROJECT KNOWLEDGE (UNTRUSTED DATA)
  --- [Source: lecture_01.pdf — Page 4] ---
  [Extracted PDF text chunks]

  ### LEARNER QUESTION
  [User input]
  ```
- Any adversarial attempts to override rules or exfiltrate prompts are neutralized by the fixed system instruction boundary.

---

## 3. Observability & AI Spend Tracking

Every AI invocation records the following attributes into `ai_request_logs`:
- `feature`: `tutor_chat`, `quiz_generator`, `rubric_evaluator`.
- `provider`: `openai`, `anthropic`, or `local`.
- `model`: e.g. `gpt-4o-mini`.
- `prompt_tokens` & `completion_tokens`.
- `latency_ms`: total wall-clock execution time.
- `cost_usd`: calculated based on published provider token rates.
- `status`: `SUCCESS`, `ERROR`, `REFUSED_LOW_EVIDENCE`.

Admin endpoints expose aggregated metrics:
- `GET /api/v1/admin/ai-metrics`: Total spend, P95 latency, refusal rate, and recent request logs.
