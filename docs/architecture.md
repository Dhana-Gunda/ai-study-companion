# System Architecture Specification
## The Lenny Growth Assistant

**Document Version:** 1.0  
**Author:** Forward Deployed Engineer  
**Status:** Approved for Implementation  

---

## 1. System Topology Overview

The Lenny Growth Assistant is designed as a modular, containerized 3-tier system:

```
                  +----------------------------------------------+
                  |               Client Browser                 |
                  |  (Next.js / React + Tailwind CSS + iframe)   |
                  +----------------------------------------------+
                                       |   ^
                    HTTP / SSE (Stream)|   |
                                       v   |
                  +----------------------------------------------+
                  |             FastAPI ASGI Server              |
                  |  - Session / Chat / Artifact REST Endpoints  |
                  |  - SSE Token Streaming Engine                |
                  |  - Dynamic Provider Dispatcher               |
                  +----------------------------------------------+
                         /         |              \
                        /          |               \
                       v           v                v
         +-----------------+  +-----------------+  +----------------------+
         | pgvector / DB   |  | Ollama (Local)  |  | Cloud Providers      |
         | PostgreSQL 16   |  | llama3.2:3b     |  | - Anthropic Claude   |
         | + pgvector HNSW |  | (localhost:     |  | - OpenAI GPT-4o      |
         | (or SQLite fb)  |  |  11434)         |  | (API Fallback)       |
         +-----------------+  +-----------------+  +----------------------+
```

---

## 2. Database Schema (PostgreSQL + pgvector)

The database utilizes standard relational tables for session persistence and the `pgvector` extension for sub-second semantic retrieval.

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Chat Sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Chat Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]'::jsonb, -- Array of cited transcript chunks
    provider VARCHAR(64) NOT NULL DEFAULT 'ollama',
    model VARCHAR(64) NOT NULL DEFAULT 'llama3.2:3b',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_session ON messages(session_id);

-- 3. Generated Artifacts
CREATE TABLE artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    artifact_type VARCHAR(32) NOT NULL CHECK (artifact_type IN ('markdown', 'html')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_artifacts_message ON artifacts(message_id);

-- 4. Transcript Chunks with pgvector
CREATE TABLE transcript_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_slug VARCHAR(255) NOT NULL,
    episode_title VARCHAR(512) NOT NULL,
    guest_name VARCHAR(255) NOT NULL,
    timestamp_ref VARCHAR(64),          -- e.g. "00:14:22" or topic segment
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    token_count INT NOT NULL,
    embedding vector(384) NOT NULL      -- Matches all-MiniLM-L6-v2 (384-d)
);

-- High-performance HNSW index for cosine distance
CREATE INDEX idx_transcript_chunks_hnsw 
ON transcript_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### Automatic SQLite Fallback Mode
When running in local development environments without an active Docker daemon or PostgreSQL server, the backend transparently initializes an embedded SQLite database (`lenny_assistant.db`) and evaluates cosine similarity in-memory using vectorized NumPy computations, ensuring a zero-friction evaluation path.

---

## 3. Ingestion & Retrieval Pipeline

```
[Raw Transcript Files]
        |
        v
[Loader & Metadata Parser] -> Guest, Title, Date, Speaker Timestamps
        |
        v
[Recursive Chunker]       -> 500-800 tokens, 100-token overlap, speaker boundary preservation
        |
        v
[Embedding Model]         -> 384-dimensional dense vectors (all-MiniLM-L6-v2 / Ollama)
        |
        v
[pgvector / HNSW Store]   -> Indexed for fast cosine similarity
```

### Retrieval Query Execution
1. Incoming user query is vectorized via the embedding model.
2. Cosine similarity query is executed against `transcript_chunks`:
   $$\text{similarity} = 1 - (\text{embedding} \Leftrightarrow \vec{q})$$
3. Results are filtered by threshold ($\ge 0.60$) and sorted descending, taking the top $K=5$ segments.
4. If no segments pass the threshold, the system prompt triggers an out-of-context fallback:
   > *"I do not have sufficient information in Lenny's podcast archive to answer this."*

---

## 4. Multi-Provider LLM & Routing Layer

```
                        [Client Chat Request]
                                  |
                                  v
                    [Provider Factory / Router]
                     /                       \
        (mode = 'ollama')                 (mode = 'claude' / 'openai')
                  v                                    v
       [OllamaProvider Driver]             [CloudProvider Driver]
       - Base URL: localhost:11434         - Anthropic Claude 3.5 Sonnet
       - Model: llama3.2:3b                - OpenAI GPT-4o / GPT-4o-mini
       - SSE Stream Generator              - SSE Stream Generator
                  \                                   /
                   v                                 v
                     [Unified Async Token Stream]
```

### Contract: `BaseLLMProvider`
All providers implement an abstract async generator:
```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        pass
```

---

## 5. Dedicated Ship 30 for 30 Skill Engine

The `ship30_writer` skill encodes the proven atomic essay mechanics:
1. **The Headline & The Hook:** Direct promise, counterintuitive hook, speed to value.
2. **The Rhythm (1-3-1 Cadence):** One single punchy sentence, followed by a short 3-sentence explanatory block, closed with a single takeaway line.
3. **Skimmability:** Markdown H2/H3 subheadings, bold visual anchors on the first 2–4 words of every bullet point.
4. **Target Volume:** Approximately 1,250 words structured into 4 distinct phases:
   - *Phase 1: The Trap* (Why traditional advice fails).
   - *Phase 2: The Mental Model* (The guest's proprietary framework).
   - *Phase 3: The 4-Step Playbook* (Exact step-by-step execution).
   - *Phase 4: The Golden Rule* (Summary checklist for tomorrow morning).
5. **Grounding:** Quotes, frameworks, and metrics strictly attributed to podcast guests.

---

## 6. Artifact Generation & Security Isolation

### Tag Protocol
When generating standalone documents or code, the model wraps them in structured XML tags:
```xml
<artifact type="html" title="Interactive PLG ROI Calculator">
<!DOCTYPE html>
<html>
...
</html>
</artifact>
```
or
```xml
<artifact type="markdown" title="LNO Prioritization Executive Brief">
# Executive Brief
...
</artifact>
```

### Security Sandboxing
1. **DOMPurify Sanitization:** HTML strings are sanitized to eliminate malicious vector scripts while preserving inline CSS styling and layout scripts.
2. **Iframe Sandboxing:** Rendered inside `<iframe sandbox="allow-scripts" srcdoc="..."></iframe>`.
   - **Crucial Security Decision:** The `allow-same-origin` token is **omitted**.
   - **Why:** Without `allow-same-origin`, the untrusted iframe executes scripts in an isolated, unique origin. It cannot access `window.parent`, cannot read `localStorage`/cookies, and cannot make authenticated requests to the host application's backend.

---

## 7. Observability, Logging & Resilience

- **Structured JSON Logging:** Every request is stamped with a unique `request_id`, execution duration, provider name, and token count.
- **Resilience Strategy:**
  - *Ollama Unavailable:* If the local Ollama daemon is offline or returns a connection error, the backend yields a descriptive status message guiding the user to start `ollama serve` or run `ollama pull llama3.2:3b`.
  - *Cloud Key Missing:* If the user selects Claude or OpenAI without providing an API key, the system falls back to Ollama or alerts the user with a 400 error.
  - *Database Failure:* If Postgres is down, SQLite fallback activates seamlessly without crashing the ASGI worker.
