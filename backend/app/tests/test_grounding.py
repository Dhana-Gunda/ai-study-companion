import pytest
from app.modules.ai.guardrails import EvidenceGuardrail
from app.modules.ai.context import ContextComposer

def test_evidence_guardrail_empty_evidence():
    assert EvidenceGuardrail.has_sufficient_evidence([]) is False
    assert EvidenceGuardrail.has_sufficient_evidence(None) is False

def test_evidence_guardrail_sufficient_evidence():
    evidence = [
        {"chunk_id": "c1", "content": "Gradient descent minimizes MSE.", "filename": "doc.pdf", "page_number": 3}
    ]
    assert EvidenceGuardrail.has_sufficient_evidence(evidence, min_chunks=1) is True

def test_refusal_message_structure():
    refusal = EvidenceGuardrail.generate_insufficient_evidence_refusal()
    assert "I do not have sufficient information" in refusal
    assert "uploaded project materials" in refusal

def test_context_composer_citation_formatting():
    evidence = [
        {"chunk_id": "c1", "content": "Weight update rule: w = w - lr * grad", "filename": "lecture_01.pdf", "page_number": 7},
        {"chunk_id": "c2", "content": "Convex optimization guarantees global minimum.", "filename": "math_notes.pdf", "page_number": 12}
    ]
    learning_context = {
        "learning_goal": "Understand gradient descent",
        "weak_concepts": ["Step size oscillation"],
        "strengths": ["Matrix multiplication"]
    }
    recent_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! Ready to learn."}
    ]

    prompt = ContextComposer.compose_tutor_prompt(
        user_message="Why does learning rate matter?",
        evidence=evidence,
        learning_context=learning_context,
        recent_history=recent_history
    )

    # Validate citations are injected into prompt
    assert "[Source: lecture_01.pdf — Page 7]" in prompt
    assert "[Source: math_notes.pdf — Page 12]" in prompt
    assert "Weight update rule" in prompt
    assert "Step size oscillation" in prompt
    assert "Learner Question: Why does learning rate matter?" in prompt
