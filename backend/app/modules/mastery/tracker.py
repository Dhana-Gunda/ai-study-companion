class MasteryTracker:
    """Updates concept mastery using an Exponential Moving Average (EMA) update rule."""

    @staticmethod
    def calculate_new_mastery(current_score: float, new_evidence_score: float, alpha: float = 0.3) -> float:
        # EMA: Mastery = alpha * new + (1 - alpha) * current
        updated = (alpha * new_evidence_score) + ((1.0 - alpha) * current_score)
        return max(0.0, min(1.0, round(updated, 3)))
