from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class QuizStartRequest(BaseModel):
    project_id: str
    target_concepts: Optional[List[str]] = None
    question_count: int = Field(default=5, ge=1, le=20)

class QuizQuestionOut(BaseModel):
    id: str
    session_id: str
    question_type: str
    prompt: str
    options: Optional[List[str]] = None
    concept_id: Optional[str] = None

class AnswerSubmitRequest(BaseModel):
    question_id: str
    user_answer: str

class RubricEvaluation(BaseModel):
    score: float
    understanding_level: str
    strengths: List[str]
    missing_concepts: List[str]
    constructive_feedback: str
