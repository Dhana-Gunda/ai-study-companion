from typing import Dict, Any, List

class RecommendationEngine:
    """Generates the single most actionable next step answering: 'What should I do next?'"""

    @staticmethod
    def generate_recommendation(
        learning_goal: str,
        weak_concepts: List[str],
        recent_activity: str
    ) -> Dict[str, str]:
        if weak_concepts:
            target = weak_concepts[0]
            return {
                "action_type": "REVIEW_MATERIAL",
                "headline": f"Reinforce your understanding of '{target}'",
                "description": f"You've shown promising progress toward '{learning_goal}', but '{target}' questions revealed gaps. Review related sections and complete a quick 3-question drill.",
                "cta_label": f"Review {target}"
            }
        return {
            "action_type": "CONTINUE_TUTOR",
            "headline": "Advance your learning journey",
            "description": "All core concepts are currently stable! Continue exploring with your AI Tutor or take an adaptive challenge quiz.",
            "cta_label": "Start Next Quiz"
        }
