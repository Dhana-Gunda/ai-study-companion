# AI Study Companion
> **AI-Powered Learning & Growth Workspace**  
> Full-Stack Prototype Architecture with Grounded AI Tutor, Adaptive Assessments, Concept Mastery, and Admin Observability.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=flat-square&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.3-black.svg?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_with_pgvector-4169E1.svg?style=flat-square&logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Redis](https://img.shields.io/badge/Redis-7.0_Alpine-DC382D.svg?style=flat-square&logo=redis&logoColor=white)](https://redis.io)

---

## 1. Product Overview

**AI Study Companion** is a persistent, contextual, and measurable learning workspace designed to help users understand, practice, measure, and continuously improve a skill or area of knowledge.

The platform continuously answers three fundamental questions for the learner:
1. **What am I learning?** (Spaces, Projects, goals, learning materials, extracted concepts)
2. **How well am I learning it?** (Adaptive quizzes, open-ended rubric evaluations, mistake tracking, concept mastery)
3. **What should I do next?** (Growth trends, targeted material review, and personalized next-action recommendations)

---

## 2. System Architecture

```
Frontend (Next.js 14 App Router + Tailwind + shadcn/ui)
│  ├── User Home & Spaces/Projects Hub
│  ├── Grounded AI Tutor (SSE streaming + page citations)
│  ├── Adaptive Quiz Runner (MCQ + open-ended rubric evaluation)
│  ├── Concept Mastery & Growth Trajectory Dashboard
│  └── Platform Admin & AI Observability Dashboard
│
▼ (HTTP / SSE)
FastAPI Backend (Application & Security Gateway)
│  ├── Security & Multi-Tenant Project Isolation Middleware
│  └── API v1 Routers (/auth, /spaces, /projects, /materials, /tutor, /quizzes, /mastery, /admin, /health)
│
▼
Business Logic Modules & Background Workers (Redis + ARQ)
│  ├── Learning Module: Spaces, Projects, Materials lifecycle
│  ├── Knowledge Module: PDF parsing (PyMuPDF), chunking, pgvector retrieval
│  ├── AI Module: LLM abstraction (OpenAI / Anthropic / Ollama), Context Composer, Refusal Guardrail
│  ├── Assessment Module: Adaptive question selector, Rubric grading engine
│  ├── Mastery & Growth: EMA mastery computation, trend analysis, next-action engine
│  ├── Analytics Module: Immutable event bus, project & global statistics
│  └── Admin Module: AI token spend, latency percentiles, system health
│
▼
Data Layer
├── PostgreSQL 16 (Relational: users, spaces, projects, quizzes, events)
├── pgvector Extension (Vector Store: document_chunks with 1536-dim embeddings)
├── Persistent Learning Context Store (JSONB learner state per project)
├── Redis 7 (Background task queue & session caching)
└── Storage (Local filesystem / S3-compatible raw PDF storage)
```

---

## 3. Quickstart & Deployment

### Option A: Complete Stack via Docker Compose (Recommended)

To start PostgreSQL 16 (with `pgvector` enabled), Redis, FastAPI backend, and Next.js frontend:

```bash
# 1. Clone repository and navigate to project root
cd newProject

# 2. Setup your environment variables
cp .env.example .env

# 3. Launch all services
docker-compose up --build
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API & Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Stack Health Probe:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Option B: Local Development (Step-by-Step)

#### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Docker** (for Postgres & Redis, or run local instances)

#### 1. Start Infrastructure (PostgreSQL with pgvector & Redis)
```bash
docker-compose up -d db redis
```

#### 2. Start Backend API
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Start Frontend
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 4. Key Endpoints & Verification

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root API metadata & service links |
| `GET` | `/api/v1/health` | Deep health probe verifying Postgres, `pgvector`, Redis, and AI providers |
| `GET` | `/docs` | Interactive Swagger / OpenAPI documentation |
| `POST` | `/api/v1/spaces` | Create a broad study Space |
| `POST` | `/api/v1/projects` | Create a focused Project with learning goals |
| `POST` | `/api/v1/materials/upload` | Upload PDF learning material for async ingestion |
| `POST` | `/api/v1/tutor/chat` | Grounded chat with citations & low-evidence refusal |
| `POST` | `/api/v1/quizzes/start` | Start adaptive assessment targeting weak concepts |
| `GET` | `/api/v1/mastery` | Concept mastery scores & growth trends |
| `GET` | `/api/v1/admin/ai-metrics` | Telemetry on AI invocations, token usage, latency, and cost |

---

## 5. Automated Tests

To run the backend test suite:
```bash
cd backend
pytest app/tests/ -v
```
Tests validate:
- Deep health check and service connectivity probe
- Multi-tenant project boundary validation and security gate
