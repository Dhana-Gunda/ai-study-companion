from typing import List, Dict, Any
import random

class AdaptiveAssessmentEngine:
    """Selects concepts and question difficulty based on student mastery & error history."""

    @staticmethod
    def select_target_concept(concept_mastery_list: List[Dict[str, Any]]) -> str:
        if not concept_mastery_list:
            return "General Core Concepts"

        # Prioritize concepts requiring attention (< 50%) or stable (50-75%)
        attention = [c for c in concept_mastery_list if c.get("mastery_score", 0) < 0.50]
        if attention:
            return random.choice(attention)["concept_name"]

        stable = [c for c in concept_mastery_list if c.get("mastery_score", 0) < 0.80]
        if stable:
            return random.choice(stable)["concept_name"]

        return random.choice(concept_mastery_list)["concept_name"]
