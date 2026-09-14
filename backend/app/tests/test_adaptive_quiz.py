import pytest
from app.modules.assessment.engine import AdaptiveAssessmentEngine
from app.modules.mastery.tracker import MasteryTracker
from app.modules.mastery.growth import GrowthAnalyzer
from app.modules.mastery.recommender import RecommendationEngine

def test_adaptive_concept_selection_prioritizes_attention():
    concept_mastery = [
        {"concept_name": "Linear Models", "mastery_score": 0.90},
        {"concept_name": "Loss Functions", "mastery_score": 0.75},
        {"concept_name": "Gradient Descent", "mastery_score": 0.35},
    ]
    selected = AdaptiveAssessmentEngine.select_target_concept(concept_mastery)
    assert selected == "Gradient Descent"

def test_ema_mastery_calculation():
    # Formula: 0.3 * new + 0.7 * current
    current = 0.50
    new_evidence = 1.00
    expected = 0.3 * 1.00 + 0.7 * 0.50  # 0.30 + 0.35 = 0.65
    updated = MasteryTracker.calculate_new_mastery(current, new_evidence, alpha=0.3)
    assert updated == pytest.approx(expected, 0.001)

def test_ema_mastery_bounds():
    assert MasteryTracker.calculate_new_mastery(0.0, -0.5) == 0.0
    assert MasteryTracker.calculate_new_mastery(1.0, 1.5) == 1.0

def test_growth_trend_improving():
    trend = GrowthAnalyzer.determine_trend(current_score=0.85, previous_score=0.70)
    assert trend == "IMPROVING"

def test_growth_trend_attention():
    trend_low = GrowthAnalyzer.determine_trend(current_score=0.45, previous_score=0.50)
    assert trend_low == "ATTENTION"

    trend_drop = GrowthAnalyzer.determine_trend(current_score=0.60, previous_score=0.75)
    assert trend_drop == "ATTENTION"

def test_growth_trend_stable():
    trend = GrowthAnalyzer.determine_trend(current_score=0.72, previous_score=0.70)
    assert trend == "STABLE"

def test_recommendation_with_weak_concepts():
    rec = RecommendationEngine.generate_recommendation(
        learning_goal="Pass Machine Learning Exam",
        weak_concepts=["Gradient Descent"],
        recent_activity="Completed quiz"
    )
    assert rec["action_type"] == "REVIEW_MATERIAL"
    assert "Gradient Descent" in rec["headline"]
    assert "Review Gradient Descent" in rec["cta_label"]

def test_recommendation_when_all_stable():
    rec = RecommendationEngine.generate_recommendation(
        learning_goal="Pass Machine Learning Exam",
        weak_concepts=[],
        recent_activity="All concepts solid"
    )
    assert rec["action_type"] == "CONTINUE_TUTOR"
    assert rec["cta_label"] == "Start Next Quiz"
