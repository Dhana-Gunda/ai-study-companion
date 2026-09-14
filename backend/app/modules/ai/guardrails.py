from typing import List, Dict, Any

class EvidenceGuardrail:
    """Verifies that retrieved evidence meets minimum threshold before generating answers."""

    @staticmethod
    def has_sufficient_evidence(evidence: List[Dict[str, Any]], min_chunks: int = 1) -> bool:
        if not evidence or len(evidence) < min_chunks:
            return False
        return True

    @staticmethod
    def generate_insufficient_evidence_refusal() -> str:
        return (
            "I do not have sufficient information in your uploaded project materials "
            "to answer this question reliably. Please upload relevant notes or a PDF covering this topic."
        )
