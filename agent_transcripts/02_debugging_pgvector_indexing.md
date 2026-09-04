# Agent Transcript 02: Retrieval Tuning, Chunking Failures & Mitigations

**Date:** 2026-09-04  
**Role:** Forward Deployed Engineer (AI Pair Programmer)  
**Task:** Tuning RAG Grounding, Chunking Heuristics, and Security Isolation  

---

## 1. Failed Attempts and How We Corrected Them

### Issue 1: Naive Fixed-Length Text Chunking Destroyed Conversational Context
- **Symptom:** Initially, splitting transcripts using arbitrary 500-token windows severed Lenny's questions from the guest's answers. In several test queries, the retriever returned Lenny introducing a topic, but lost the guest's specific response and framework.
- **Root Cause:** Podcast transcripts are dialogues, not static articles. Fixed-length chunking arbitrarily cut across speaker transitions.
- **Correction:** Implemented a dialogue-aware chunker in `backend/app/rag/chunker.py`. Chunks now prioritize splitting along speaker boundaries (`Speaker: ...`), prepend the episode title and guest name as a metadata header inside each chunk, and maintain a 100-token sliding overlap.
- **Verification:** Verified that queries for "Elena Verna freemium" consistently retrieve both the question context and Elena's complete operational breakdown.

### Issue 2: Small Local Models (3B / 7B) Hallucinating on Unrelated Topics
- **Symptom:** When prompted with an off-topic question (*"How do I bake sourdough bread?"*), local Ollama models ignored the lack of context and generated general baking instructions rather than adhering to the persona.
- **Root Cause:** Smaller parameter models have weaker instruction-following tendencies when given empty or low-relevance retrieval context.
- **Correction:** 
  1. Implemented a strict cosine similarity threshold ($\text{threshold} \ge 0.60$) in `TranscriptRetriever`.
  2. If all retrieved chunks score below this threshold, the retriever flags the context as empty.
  3. The system prompt incorporates an unambiguous guardrail rule:
     > *"If the provided context does not contain the answer, or if the context is empty, you MUST state: 'I do not have sufficient information in Lenny's podcast archive to answer this.' Do NOT use prior training data to invent answers."*
- **Verification:** Out-of-domain test queries now immediately and consistently return the graceful rejection statement.

### Issue 3: Untrusted HTML Artifact Rendering Vulnerabilities
- **Symptom:** An LLM generating an HTML artifact could theoretically inject `<script>` tags that access `window.parent.localStorage` or trigger cross-site scripting (XSS) against the host application.
- **Root Cause:** Rendering raw HTML in standard web elements or in an un-sandboxed iframe gives the script full execution privileges in the origin context.
- **Correction:** 
  1. We mount generated HTML inside an `<iframe>` with strict sandbox configuration: `sandbox="allow-scripts"`.
  2. We **strictly omit** `allow-same-origin`. Because `allow-same-origin` is omitted, the browser treats the iframe as a unique, opaque origin (`null`). Even if malicious JavaScript executes, it cannot access the parent window, cannot read authentication tokens or cookies, and cannot make authenticated requests to `/api/`.
  3. In addition, the content is sanitized with `DOMPurify` before insertion.
- **Verification:** Injected scripts attempting `parent.document.cookie` throw immediate browser origin errors inside the sandbox.

### Issue 4: Ship 30 for 30 Output Length & Formatting Collapse
- **Symptom:** Initial tests with prompt *"Write a Ship 30 for 30 essay"* produced a terse 350-word listicle without the distinctive rhythmic formatting or depth.
- **Root Cause:** The model lacked concrete architectural guardrails for each section of the essay.
- **Correction:** Engineered the `ship30_writer.py` skill prompt to specify 4 structural phases:
  - Phase 1: The Trap / Pain Point (Counterintuitive hook, 1-3-1 cadence).
  - Phase 2: The Mental Model (Core theory attributed to the guest).
  - Phase 3: The 4-Step Playbook (Actionable execution steps with bold visual anchors).
  - Phase 4: The Golden Rule (Immediate checklist for tomorrow morning).
  Target word count explicitly enforced at ~1,250 words.
- **Verification:** Outputs now match the viral, skimmable format of Ship 30 for 30 essays while remaining 100% grounded in podcast transcripts.
