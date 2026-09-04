# Design Specification (UI / UX)
## The Lenny Growth Assistant

**Document Version:** 1.0  
**Author:** Forward Deployed Engineer  
**Status:** Approved for Implementation  

---

## 1. UI/UX Principles & Aesthetic Direction

The design of The Lenny Growth Assistant is modeled after high-velocity developer & product tools like Linear and Claude:
1. **Speed & Minimalist Elegance:** Clean typography, generous whitespace, subtle borders, and zero unnecessary visual clutter.
2. **Immediate Information Hierarchy:** User questions, assistant answers, verified transcript citations, and generated artifacts have distinct, predictable visual weights.
3. **Claude-Style Artifact Workspace:** Rather than trapping long documents or interactive tools inside the chat stream, artifacts automatically open into a dedicated side-by-side workbench.
4. **Transparent System State:** Real-time visibility into whether the model is searching the transcript database, thinking, streaming tokens, or compiling an artifact.

---

## 2. Information Architecture & Layout

The interface is structured into three primary horizontal zones on desktop:

```
+---------------------------------------------------------------------------------------+
|  TOP NAVIGATION: Logo | Active Session Title | Model Switcher Pill | Clear | Status   |
+-------------+---------------------------------------+---------------------------------+
|  SIDEBAR    |  CENTRAL CHAT PANE                    |  ARTIFACT VIEWER (Collapsible)  |
|             |                                       |                                 |
|  [+ New]    |  [Message History Stream]             |  [Header: Title | Copy | Close] |
|             |  - User bubble (right-aligned)        |  -----------------------------  |
|  Recent:    |  - Assistant bubble (left-aligned)    |  [Content Container]            |
|  - PLG Loop |    • Grounded answer                  |  - Markdown preview OR          |
|  - LNO Prio |    • Source citation badges [1][2]    |  - Sandboxed iframe preview     |
|  - Retention|    • [Open Artifact: "ROI Calc"]      |    (HTML / CSS / JS)            |
|             |                                       |                                 |
|  Bottom:    |  -----------------------------------  |                                 |
|  DB Status  |  [Input Bar: Textarea | Mode | Send]  |                                 |
|  v1.0.0     |  Suggestions: [Ship 30 Essay] [PLG]   |                                 |
+-------------+---------------------------------------+---------------------------------+
```

### Layout Breakdown
1. **Collapsible Navigation Sidebar (260px):**
   - Button: `+ New Chat` (generates fresh session UUID).
   - Chronological session list with active indicators and delete buttons.
   - Status indicators: Database connection status and active retrieval index count.
2. **Central Chat Workspace (Flexible / 600–800px max reading width):**
   - Clean message stream with Markdown formatting.
   - Grounded Source Badges: Clickable tags displaying guest name and timestamp (e.g. `[Elena Verna, 00:14:20]`).
   - Actionable Suggestion Chips for first-time evaluators (`"Explain Shreyas Doshi's LNO framework"`, `"Generate a Ship 30 for 30 essay on B2B product-led growth"`).
3. **Collapsible Artifact Viewer (Flexible 45–50% screen width when open):**
   - Header with artifact title, format badge (`HTML` or `MARKDOWN`), "Copy Code" button, and "Close" button.
   - Seamless live rendering of untrusted HTML/CSS in a sandboxed iframe.

---

## 3. Design Tokens & Visual Hierarchy

### Color Palette (Tailwind-compatible)
- **Background Surface (`bg-zinc-950` / `bg-white`):** Deep charcoal dark theme with high-contrast neutral light mode.
- **Card & Bubble Surface (`bg-zinc-900` / `bg-zinc-100`):** Elevated surfaces for message bubbles and sidebars.
- **Borders (`border-zinc-800` / `border-zinc-200`):** Subtle 1px dividers.
- **Primary Accent (`indigo-500` / `indigo-600`):** Used for primary buttons, active session pills, and focus rings.
- **Citation Badges (`emerald-500` / `emerald-600`):** Used for verified source citations to evoke truth and trust.
- **Artifact Accent (`amber-500` / `amber-600`):** Highlights generated artifacts and special skills.

### Typography
- **Font Family:** Inter or system-ui sans-serif for UI; JetBrains Mono or Fira Code for code blocks and artifacts.
- **Scale:**
  - H1 / Page Header: `text-xl font-semibold`
  - Body Chat: `text-sm leading-relaxed text-zinc-200`
  - Metadata / Badges: `text-xs font-mono`

---

## 4. Key Interaction States

| State | Central Chat | Top Bar | Artifact Pane |
|---|---|---|---|
| **Idle / Empty Session** | Centered hero greeting + 4 clickable suggestion prompt cards | Session title: *"New Chat"* | Hidden (collapsed) |
| **Retrieving Transcripts** | Pulsing badge: *"Searching Lenny's Podcast transcripts..."* | Spinner in model pill | Hidden |
| **Streaming Response** | Blinking cursor at end of text; real-time token rendering | Active streaming indicator | Hidden |
| **Artifact Detected** | Message renders an inline card: *"Artifact Created: Click to view"* | Model badge: Success | Automatically slides open from right with smooth transition |
| **Out-of-Domain Query** | Polite message explaining lack of podcast context | Normal | Hidden |
| **Error / Offline Ollama** | Red toast alert with exact command to run: `ollama run llama3.2:3b` | Warning icon | Hidden |

---

## 5. Responsive Behavior

- **Desktop ($\ge 1024\text{px}$):** Full 3-pane experience. Opening an artifact splits the screen 50/50 between chat and artifact view.
- **Tablet ($768\text{px}\text{--}1023\text{px}$):** Sidebar collapses into a drawer; chat and artifact share 50/50 split or toggle via tabs.
- **Mobile ($< 768\text{px}$):** Tabbed interface with two main tabs: `Chat` and `Artifact`. When an artifact is created, a floating bottom banner prompts the user to switch tabs to view the artifact.

---

## 6. Accessibility (a11y) Considerations

1. **Keyboard Navigability:** Tab order moves logically: Sidebar $\to$ New Chat $\to$ Message history $\to$ Input textarea $\to$ Send button $\to$ Artifact controls.
2. **Screen Reader Support:** All buttons have explicit `aria-label` attributes (e.g. `aria-label="Copy artifact code to clipboard"`, `aria-label="Select Ollama provider"`).
3. **High Contrast:** All text meets WCAG AA contrast ratio ($\ge 4.5:1$).
4. **Iframe Isolation:** Untrusted iframe has `title="Generated Artifact Sandbox"` and does not interfere with the outer page focus trap.
