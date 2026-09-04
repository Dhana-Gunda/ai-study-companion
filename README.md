# The Lenny Growth Assistant
> Enterprise-grade, full-stack Retrieval-Augmented Generation (RAG) assistant unlocking operational product and growth wisdom from **Lenny’s Podcast** transcripts.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=flat-square&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.3-black.svg?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_with_pgvector-4169E1.svg?style=flat-square&logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-white.svg?style=flat-square&logo=ollama&logoColor=black)](https://ollama.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

---

## 1. Overview & Key Capabilities

The Lenny Growth Assistant empowers Product Managers, Growth Leads, and Founders to extract actionable frameworks from over 200+ podcast interviews with tech luminaries (e.g. Shreyas Doshi, Elena Verna, Brian Chesky).

### Core Features
1. **Grounded Question Answering:** Strictly retrieves relevant transcript dialogue using vector cosine similarity. Every factual assertion cites the guest name, episode title, and timestamp.
2. **Missing Information Guardrails:** Out-of-domain queries trigger a graceful rejection statement (*"I do not have sufficient information in Lenny's podcast archive to answer this"*), preventing LLM hallucinations.
3. **Dedicated Ship 30 for 30 Essay Skill:** Transforms insights into a structured, ~1,250-word essay following the 1-3-1 sentence cadence, bold bullet anchors, and tactical checklists.
4. **Claude-Style In-App Artifact Viewer:** Renders Markdown briefs or complete interactive HTML/CSS/JS widgets side-by-side with the chat.
5. **Secure Sandboxing:** Untrusted generated HTML is isolated in an `<iframe>` configured with `sandbox="allow-scripts"` (strictly omitting `allow-same-origin`) and pre-sanitized with DOMPurify.
6. **Dynamic Dual-Engine Model Switching:** Run locally using **Ollama** (`llama3.2:3b`, `llama3.1:8b`, `mistral:7b`) for zero-cost private demos, or toggle in real-time to **Anthropic Claude 3.5 Sonnet** or **OpenAI GPT-4o** without restarting the server.
7. **Zero-Friction Fallback:** Primary persistence in PostgreSQL with `pgvector`; automatically falls back to async SQLite with in-memory vector matching for zero-dependency local runs.

---

## 2. System Architecture

```
                                [Browser UI]
                       (Next.js 14 + Tailwind CSS)
                       /                        \
          [Central Chat Pane]              [Artifact Viewer]
          (Streaming SSE Tokens)           (Sandboxed Iframe)
                       \                        /
                        v                      v
                  +-----------------------------------+
                  |        FastAPI ASGI Backend       |
                  |  - Sessions, Chat & Artifact APIs |
                  |  - Hybrid Vector Retriever        |
                  |  - Ship 30 for 30 Skill Engine    |
                  +-----------------------------------+
                         /          |             \
                        /           |              \
                       v            v               v
           +----------------+  +-------------+  +--------------------+
           |  PostgreSQL 16 |  |   Ollama    |  |  Cloud Providers   |
           |   + pgvector   |  | (llama3.2)  |  |  - Claude 3.5      |
           |  (or SQLite fb)|  | (Local 3B)  |  |  - OpenAI GPT-4o   |
           +----------------+  +-------------+  +--------------------+
```

For complete architectural details and database schemas, see [`docs/architecture.md`](docs/architecture.md).  
For product strategy and discovery brief, see [`docs/PRD.md`](docs/PRD.md).  
For UI/UX design rationale and interaction states, see [`docs/design.md`](docs/design.md).  

---

## 3. Quickstart & Deployment

### Option A: One-Command Startup with Docker Compose (Recommended)

Ensure Docker Desktop is running, then execute:

```bash
# 1. Clone or navigate to the repository
cd newProject

# 2. Copy environment template
cp .env.example .env

# 3. Launch PostgreSQL (with pgvector), Backend, and Frontend
docker-compose up --build
```

- **Frontend:** Visit `http://localhost:3000`
- **Backend API Docs:** Visit `http://localhost:8000/docs`
- **Health Probe:** Visit `http://localhost:8000/api/health`

---

### Option B: Local Development (Without Docker)

You can run the application directly on your machine. The backend will automatically use its embedded SQLite database fallback if PostgreSQL is not active.

#### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Ollama** installed and running:
  ```bash
  ollama serve
  ollama pull llama3.2:3b
  ```

#### 1. Start the Backend
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Ingest bundled seed transcripts into the database:
python scripts/ingest.py

# Start FastAPI server:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Start the Frontend
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 4. Ingesting Transcripts

The project comes pre-seeded with high-impact transcripts (Elena Verna on PLG, Shreyas Doshi on the LNO framework, and Brian Chesky on Founder Mode) located in `backend/data/transcripts/`.

To re-index or add new transcripts:
```bash
cd backend
# Optional: Download additional transcripts from GitHub
python scripts/download_transcripts.py

# Run chunking, vector embedding, and indexer:
python scripts/ingest.py
```

---

## 5. Model Provider Configuration

You can seamlessly switch models in the navigation bar dropdown at any time:

| Provider | Model | Setup Instructions |
|---|---|---|
| **Ollama (Local - Mandatory Demo)** | `llama3.2:3b` | Run `ollama run llama3.2:3b` |
| **Anthropic Claude (Cloud)** | `claude-3-5-sonnet-20241022` | Set `ANTHROPIC_API_KEY=your_key` in `.env` |
| **OpenAI (Cloud)** | `gpt-4o` | Set `OPENAI_API_KEY=your_key` in `.env` |

---

## 6. Running Automated Tests

Run the complete backend test suite using `pytest`:

```bash
cd backend
pytest tests/ -v
```

The test suite validates:
- `test_api.py`: Health endpoint status, session CRUD, and message serialization.
- `test_retrieval.py`: Dialogue-aware chunking, embedding generation, cosine similarity, and out-of-domain threshold rejection.
- `test_providers.py`: Provider dynamic factory, Ship 30 for 30 prompt constraints (1,250 words, 1-3-1 cadence), and artifact XML extraction.

---

## 7. Security & Artifact Sandboxing

To satisfy zero-trust security expectations when generating and executing HTML/JS code artifacts:
1. **Sanitization:** Raw HTML generated by the LLM is sanitized via `DOMPurify` to eliminate malicious vectors.
2. **Iframe Sandboxing:** Rendered within `<iframe sandbox="allow-scripts">`.
3. **Origin Isolation:** We **strictly omit** `allow-same-origin`. This forces the browser to treat the iframe execution context as an opaque, isolated `null` origin. Even if malicious JavaScript runs, it cannot access the parent application's DOM, `localStorage`, session cookies, or trigger unauthorized API requests.

---

## 8. Troubleshooting & Operational Handoff

| Issue | Cause | Solution |
|---|---|---|
| *"Ollama Connection Failed"* in chat | Ollama daemon not running | Run `ollama serve` in a terminal window. |
| *"Model not found on Ollama"* | Model weights not downloaded | Run `ollama pull llama3.2:3b` (or your configured model). |
| *"Anthropic API Key Missing"* | Switched to Claude without key in `.env` | Add `ANTHROPIC_API_KEY` to `.env` or switch back to Ollama in the navbar. |
| Postgres connection refused | Local Postgres not running | No action required! The application automatically switches to SQLite fallback. |

---

## 9. Deliverables Directory

- **PRD:** [`docs/PRD.md`](docs/PRD.md)
- **Architecture Spec:** [`docs/architecture.md`](docs/architecture.md)
- **Design Spec:** [`docs/design.md`](docs/design.md)
- **Agent Transcripts & Debug Logs:** [`agent_transcripts/`](agent_transcripts/)
- **Video Demo Script:** [`demo_script.md`](demo_script.md)
