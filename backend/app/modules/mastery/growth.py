from typing import Literal

class GrowthAnalyzer:
    """Classifies learning trend into IMPROVING, STABLE, or ATTENTION."""

    @staticmethod
    def determine_trend(current_score: float, previous_score: float) -> str:
        delta = current_score - previous_score
        if delta >= 0.10:
            return "IMPROVING"
        elif current_score < 0.50 or delta <= -0.10:
            return "ATTENTION"
        return "STABLE"
