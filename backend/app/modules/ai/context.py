from typing import Dict, Any, List

class ContextComposer:
    """Combines session conversation, retrieved evidence, and persistent learner context into a unified prompt."""

    @staticmethod
    def compose_tutor_prompt(
        user_message: str,
        evidence: List[Dict[str, Any]],
        learning_context: Dict[str, Any],
        recent_history: List[Dict[str, str]]
    ) -> str:
        prompt_parts = []

        # 1. Persistent Learner Context
        prompt_parts.append("### LEARNER PROFILE & CONTEXT:")
        prompt_parts.append(f"- Goal: {learning_context.get('learning_goal', 'General Study')}")
        prompt_parts.append(f"- Weak Concepts: {', '.join(learning_context.get('weak_concepts', ['None identified']))}")
        prompt_parts.append(f"- Known Strengths: {', '.join(learning_context.get('strengths', ['None identified']))}")
        prompt_parts.append("")

        # 2. Retrieved Material Evidence
        prompt_parts.append("### RETRIEVED PROJECT KNOWLEDGE:")
        if not evidence:
            prompt_parts.append("[NO EVIDENCE FOUND IN PROJECT MATERIALS]")
        else:
            for item in evidence:
                prompt_parts.append(f"--- [Source: {item['filename']} — Page {item['page_number']}] ---")
                prompt_parts.append(item["content"])
                prompt_parts.append("")

        # 3. Recent Dialogue History
        if recent_history:
            prompt_parts.append("### RECENT CONVERSATION:")
            for msg in recent_history[-4:]:
                prompt_parts.append(f"{msg['role'].capitalize()}: {msg['content']}")
            prompt_parts.append("")

        # 4. Current User Question
        prompt_parts.append(f"Learner Question: {user_message}")
        prompt_parts.append("AI Tutor:")

        return "\n".join(prompt_parts)
