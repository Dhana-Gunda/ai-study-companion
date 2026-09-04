# Video Demo Script (2–3 Minutes)
## The Lenny Growth Assistant

**Presenter:** Forward Deployed Engineer  
**Setting:** Camera enabled, screen sharing application running on `http://localhost:3000` with terminal showing Ollama running locally.

---

### [0:00 - 0:30] Scene 1: Problem Statement & Discovery Framing
- **Visual:** Camera on face, then transition to browser showing The Lenny Growth Assistant interface.
- **Script:**
  > *"Hi everyone, I'm presenting The Lenny Growth Assistant—an AI copilot built for product and growth leaders to unlock the operational wisdom inside 200+ episodes of Lenny’s Podcast.*
  >
  > *The core problem we tackled is that knowledge from top tech operators like Shreyas Doshi, Elena Verna, and Brian Chesky is trapped in 500+ hours of audio. Generic LLMs hallucinate tactics without attribution, and converting insights into usable assets takes high prompt friction.*
  >
  > *Our solution gives teams strictly grounded answers with verified citations, a dedicated Ship 30 for 30 essay engine, and a Claude-style sandboxed Artifact Viewer."*

---

### [0:30 - 1:15] Scene 2: Grounded Q&A & Local Ollama Execution
- **Visual:** Point to the top navbar showing `Ollama: llama3.2:3b (Local)` active in green. Click the suggestion card: *"What does Elena Verna say about B2B Product-Led Growth, Product-Led Sales, and freemium retention?"*
- **Script:**
  > *"Notice first: I am running entirely on my local machine using Ollama with the llama3.2 3B parameter model—no external cloud calls, zero data egress.*
  >
  > *As the answer streams via Server-Sent Events, look at the citation badges at the bottom of the response. The assistant specifically cites Elena Verna from Episode 68 at timestamp 00:08:15 for freemium versus trial dynamics, and 00:15:05 for Product-Qualified Leads.*
  >
  > *If I were to ask an out-of-domain question, our strict cosine similarity threshold stops hallucination and politely informs the user that the podcast archive does not contain the answer."*

---

### [1:15 - 1:55] Scene 3: Ship 30 for 30 Content Engine & Sandboxed Artifact Viewer
- **Visual:** Switch mode to `Ship 30 for 30 Skill` and ask: *"Write a Ship 30 for 30 essay on Shreyas Doshi's LNO Framework."* Next, ask for an interactive ROI calculator in `Artifact Tool` mode. Show the right panel sliding open side-by-side.
- **Script:**
  > *"Next, let's explore our custom skills. Growth teams don't just want chat; they need shareable content and interactive tools.*
  >
  > *Here, our Ship 30 for 30 engine creates a ~1,250-word essay following the 1-3-1 sentence cadence, with bold visual anchors and clear operational takeaways.*
  >
  > *And when we request an interactive tool, the Claude-style Artifact Viewer opens side-by-side. You can see this interactive PLG ROI calculator rendered live in HTML and CSS.*
  >
  > *Crucially, for security: this is rendered inside a sandboxed iframe with `sandbox='allow-scripts'` and strictly omitting `allow-same-origin`. This guarantees that even untrusted generated HTML/JS cannot access parent cookies, local storage, or session tokens."*

---

### [1:55 - 2:40] Scene 4: Key Technical Trade-Off & Operational Architecture
- **Visual:** Briefly show the model toggle dropdown switching from `Ollama` to `Claude 3.5 Sonnet`, then show the terminal with `docker-compose.yml`.
- **Script:**
  > *"Now for the key technical trade-off: Local Model Independence versus Cloud Reasoning.*
  >
  > *Local 3B/8B models provide unmatched privacy and zero API costs, but they are more susceptible to context degradation on long dialogues. To solve this, we engineered a dialogue-aware chunker that injects episode and speaker headers into every chunk before embedding into pgvector.*
  >
  > *Furthermore, we built a zero-restart provider toggle. Evaluators can switch from Ollama to Claude 3.5 Sonnet or OpenAI GPT-4o right in the UI.*
  >
  > *Finally, the entire stack—PostgreSQL with pgvector, FastAPI, and Next.js—is deployable via a single `docker-compose up` command, with automated SQLite fallback for zero-dependency local runs.*
  >
  > *Thank you, and I look forward to your feedback!"*
