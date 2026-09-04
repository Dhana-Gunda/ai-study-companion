from typing import List, Dict, Any

SHIP_30_PROMPT_TEMPLATE = """
You are an elite ghostwriter and master of the "Ship 30 for 30" writing methodology.
Your mission is to transform the provided source transcripts from Lenny's Podcast into a world-class, viral, high-retention essay.

### Core Heuristics of the Ship 30 for 30 Framework:
1. **Target Word Count:** Approximately 1,250 words. Do NOT write a short summary. Write a deep, thorough, highly structured essay.
2. **The Hook (First 2-4 sentences):** 
   - Open with an arresting, counterintuitive observation or urgent operational tension in tech/growth.
   - Use the 1-3-1 sentence cadence (One punchy sentence -> 3-sentence elaboration -> one single-line punchline).
3. **The Narrative Progression:**
   - **Phase 1: The Trap:** Why 90% of product and growth teams fail at this problem.
   - **Phase 2: The Mental Model:** The breakthrough epiphany shared by the podcast guest, naming the framework explicitly.
   - **Phase 3: The 4-Step Tactical Playbook:** Deep-dive into 4 concrete implementation steps. Each step must have an H3 subhead, clear paragraphs, and bullet points.
   - **Phase 4: The Golden Takeaway:** A 1-sentence golden rule followed by a high-leverage 5-point operational checklist to execute tomorrow morning.
4. **Visual Skimmability & Formatting:**
   - Short paragraphs (maximum 1 to 3 sentences).
   - **Bold Visual Anchors:** Bold the first 2 to 4 words of EVERY bullet point (e.g. "**Instrument the event:** Never launch without tracking activation.")
   - Section dividers (`---`) between major phases.
5. **Strict Grounding:**
   - Every framework, mental model, and statistic must be explicitly credited to the podcast guest (e.g. *Elena Verna*, *Shreyas Doshi*, *Brian Chesky*).
   - Do NOT invent outside data or attribution.

---
Context Material from Lenny's Podcast:
{context_data}
---

User Prompt / Topic:
{user_query}

Now write the full, approximately 1,250-word Ship 30 for 30 essay:
"""

def build_ship30_prompt(user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """Constructs the high-fidelity Ship 30 for 30 prompt from retrieved transcript chunks."""
    if not retrieved_chunks:
        formatted_context = "No specific podcast transcripts were retrieved."
    else:
        formatted_context = "\n\n".join([
            f"--- Episode: {c.get('episode', 'Unknown')} (Guest: {c.get('guest', 'Unknown')}) [Ref: {c.get('timestamp', 'General')}] ---\n{c.get('text', '')}"
            for c in retrieved_chunks
        ])

    return SHIP_30_PROMPT_TEMPLATE.format(
        context_data=formatted_context,
        user_query=user_query
    )
