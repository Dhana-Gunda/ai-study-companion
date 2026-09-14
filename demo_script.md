# Video Demo Script (3–5 Minutes)
## AI Study Companion — Candidate Challenge Demonstration

**Live App URL:** [https://ai-study-companion-gamma.vercel.app/](https://ai-study-companion-gamma.vercel.app/)  
**Backend Docs:** [https://ai-study-companion-backend-azlw.onrender.com/docs](https://ai-study-companion-backend-azlw.onrender.com/docs)  
**GitHub:** [https://github.com/Dhana-Gunda/ai-study-companion](https://github.com/Dhana-Gunda/ai-study-companion)  

---

### Step-by-Step Walkthrough Guide for Demo Video (PRD Section 20)

| Step # | Scene / Action | What to Show on Screen | What to Say (Script) |
|---|---|---|---|
| **1. Intro & Stack Connectivity** | Open Homepage | Show `https://ai-study-companion-gamma.vercel.app/`. Point to **Live Stack Connectivity Probe** with green checkmarks (PostgreSQL 16 + pgvector, Queue & Cache, All Services Connected). | *"Hello! Welcome to the AI Study Companion. As you can see on our live production homepage, our Next.js frontend is connected to a FastAPI backend backed by PostgreSQL 16 with pgvector on Neon and Redis."* |
| **2. Create Space** | Click **"Spaces"** in nav | Click **"Create Space"** button. Name: `Computer Science`, Description: `Core CS & AI Foundations`. | *"First, we create a broad learning Space. A Space defines the high-level knowledge domain without rigid categories."* |
| **3. Create Project** | Inside Space, click **"New Project"** | Project Name: `Intro to Machine Learning`, Learning Goal: `Master Supervised Learning and Gradient Descent`. Click Create. | *"Inside our Space, we create a focused learning Project with an explicit learning goal. The system enforces strict multi-tenant project isolation."* |
| **4. Upload Material** | Open Project ➔ **Materials Tab** | Click **"Upload PDF"**. Select sample notes / paper. | *"Now we add learning materials. The system accepts PDFs and parses them asynchronously into semantic chunks with provenance."* |
| **5. Process Material** | Show Material Status | The table shows status transition `PROCESSING` ➔ `READY` with page count. | *"Our ingestion pipeline extracts text, cleans chunks, and indexes 1536-dimensional vector embeddings into pgvector while extracting key concepts."* |
| **6. Ask AI Tutor** | Switch to **AI Tutor Tab** | Type query: *"Explain how Gradient Descent optimizes weights in linear regression."* Click Send. | *"Let's consult the AI Tutor. The tutor uses grounded RAG with Server-Sent Events for streaming."* |
| **7. Grounded Answer + Citation** | Review Tutor Response | Highlight the response streaming in, and click the source badges: `[Source: lecture_01.pdf — Page 4]`. | *"Notice the response is strictly grounded in our uploaded material, complete with page citations and similarity confidence."* |
| **8. Unsupported Question Handling** | Test Guardrail | Type query: *"How do I bake sourdough bread at home?"* | *"Watch our low-evidence guardrail in action. When similarity falls below 0.60, the tutor halts and refuses to hallucinate, politely asking for relevant materials."* |
| **9. Adaptive Quiz** | Switch to **Quiz Tab** | Click **"Start Adaptive Quiz"** (3 questions). | *"Next, we evaluate understanding. The adaptive engine queries our concept mastery store and dynamically selects questions targeting our weakest concepts."* |
| **10. Open-Ended & MCQ Assessment** | Answer Questions | Select MCQ option, type a brief answer for open-ended question. Click Submit. | *"We answer the questions. The system grades MCQs instantly and applies rubric scoring to open-ended explanations."* |
| **11. Mastery & Growth** | Switch to **Mastery Tab** | Show the interactive concept mastery bars and trend badges (`IMPROVING`, `STABLE`, `ATTENTION`). | *"Our understanding is quantified through Exponential Moving Average (EMA) mastery tracking across all extracted concepts."* |
| **12. Analytics & Next Action Recommendation** | Switch to **Overview Tab** | Point to the **Active Recommendation Card** (e.g., *"Focus on Overfitting & Regularization"* with CTA). | *"The system continuously answers 'What should I do next?' by generating targeted next-action recommendations based on our mistake patterns."* |
| **13. Admin Dashboard** | Click **"Admin"** in nav | Show `/admin` with registered users, active projects, and real-time AI observability telemetry (token usage, latency, spend). | *"Finally, the Admin Dashboard provides comprehensive observability into users, system health, and token economics across all AI interactions. Thank you!"* |
