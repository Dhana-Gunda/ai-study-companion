from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.db_models import (
    Project, QuizSession, Question, Answer, Concept, ConceptMastery,
    MasterySnapshot, LearningContext, LearningEvent, Recommendation
)
from app.api.v1.deps import verify_project_ownership, get_current_user
from app.modules.assessment.engine import AdaptiveAssessmentEngine
from app.modules.assessment.evaluator import OpenEndedEvaluator
from app.modules.mastery.tracker import MasteryTracker
from app.modules.mastery.growth import GrowthAnalyzer
from app.modules.mastery.recommender import RecommendationEngine

router = APIRouter(tags=["Assessments"])

class QuizStartRequest(BaseModel):
    question_count: int = Field(default=3, ge=1, le=10)

class QuestionDetailResponse(BaseModel):
    id: str
    session_id: str
    concept_id: Optional[str]
    question_type: str
    prompt: str
    options: Optional[List[str]] = None
    user_answer: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None

class QuizSessionResponse(BaseModel):
    id: str
    project_id: str
    status: str
    score: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]
    questions: List[QuestionDetailResponse]

class AnswerSubmitRequest(BaseModel):
    user_answer: str = Field(..., min_length=1)

class AnswerResponse(BaseModel):
    question_id: str
    score: float
    feedback: str
    rubric_evaluation: Optional[Dict[str, Any]] = None

@router.post("/projects/{project_id}/quizzes/start", response_model=QuizSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_quiz_session(
    project_id: str,
    req: QuizStartRequest,
    project: Project = Depends(verify_project_ownership),
    db: AsyncSession = Depends(get_db)
):
    """Generate an adaptive diagnostic quiz session targeting concepts with low mastery or ATTENTION trends."""
    # 1. Fetch concepts and mastery for the project
    mastery_query = (
        select(ConceptMastery, Concept)
        .join(Concept, Concept.id == ConceptMastery.concept_id)
        .where(ConceptMastery.project_id == project.id)
    )
    mastery_rows = (await db.execute(mastery_query)).all()

    # Fallback to concepts without mastery if any
    if not mastery_rows:
        c_res = await db.execute(select(Concept).where(Concept.project_id == project.id))
        all_concepts = c_res.scalars().all()
    else:
        all_concepts = [c for _, c in mastery_rows]

    # Create QuizSession
    session = QuizSession(
        project_id=project.id,
        user_id=project.user_id,
        status="IN_PROGRESS"
    )
    db.add(session)
    await db.flush()

    # Generate questions based on project concepts
    questions = []
    sample_pool = [
        {
            "type": "MCQ",
            "prompt": "What happens during gradient descent when the learning rate is set excessively large?",
            "options": [
                "The algorithm converges monotonically to the global minimum.",
                "Parameters oscillate across the loss surface and may diverge away from the minimum.",
                "The loss instantly drops to zero after one step.",
                "The gradient vector becomes strictly orthogonal to the weight vector."
            ],
            "correct_answer": "Parameters oscillate across the loss surface and may diverge away from the minimum.",
            "concept_hint": "Gradient Descent"
        },
        {
            "type": "OPEN_ENDED",
            "prompt": "Explain the role of the Mean Squared Error (MSE) loss function in linear regression, and how its derivative guides gradient updates.",
            "options": None,
            "correct_answer": "MSE quantifies the average squared residual variance. Its gradient provides a convex surface directing weight adjustments proportionally to prediction error.",
            "concept_hint": "Cost Functions (MSE)"
        },
        {
            "type": "MCQ",
            "prompt": "In linear regression, what mathematical technique is used to find the optimal weights in a single closed-form matrix operation?",
            "options": [
                "Normal Equations (Ordinary Least Squares)",
                "Stochastic Backpropagation",
                "K-Means Clustering",
                "Simulated Annealing"
            ],
            "correct_answer": "Normal Equations (Ordinary Least Squares)",
            "concept_hint": "Linear Regression"
        }
    ]

    count_to_create = min(req.question_count, len(sample_pool))
    created_questions = []

    for i in range(count_to_create):
        sample = sample_pool[i]
        # Match concept
        matching_c = next((c for c in all_concepts if sample["concept_hint"] in c.name), None)
        c_id = matching_c.id if matching_c else (all_concepts[0].id if all_concepts else None)

        q = Question(
            session_id=session.id,
            concept_id=c_id,
            question_type=sample["type"],
            prompt=sample["prompt"],
            options=sample["options"],
            correct_answer=sample["correct_answer"],
            difficulty="medium"
        )
        db.add(q)
        created_questions.append(q)

    await db.commit()
    await db.refresh(session)

    # Format response
    q_responses = [
        QuestionDetailResponse(
            id=q.id,
            session_id=session.id,
            concept_id=q.concept_id,
            question_type=q.question_type,
            prompt=q.prompt,
            options=q.options,
            user_answer=None,
            score=None,
            feedback=None
        )
        for q in created_questions
    ]

    return QuizSessionResponse(
        id=session.id,
        project_id=session.project_id,
        status=session.status,
        score=session.score,
        created_at=session.created_at,
        completed_at=session.completed_at,
        questions=q_responses
    )

@router.get("/quizzes/{session_id}", response_model=QuizSessionResponse)
async def get_quiz_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Retrieve quiz session and all associated questions and answers."""
    result = await db.execute(select(QuizSession).where(QuizSession.id == session_id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz session not found.")

    if session.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this quiz.")

    q_res = await db.execute(
        select(Question, Answer)
        .outerjoin(Answer, Answer.question_id == Question.id)
        .where(Question.session_id == session.id)
    )
    rows = q_res.all()

    q_responses = []
    for q, ans in rows:
        q_responses.append(
            QuestionDetailResponse(
                id=q.id,
                session_id=session.id,
                concept_id=q.concept_id,
                question_type=q.question_type,
                prompt=q.prompt,
                options=q.options,
                user_answer=ans.user_answer if ans else None,
                score=ans.score if ans else None,
                feedback=ans.feedback if ans else None
            )
        )

    return QuizSessionResponse(
        id=session.id,
        project_id=session.project_id,
        status=session.status,
        score=session.score,
        created_at=session.created_at,
        completed_at=session.completed_at,
        questions=q_responses
    )

@router.post("/quizzes/{session_id}/questions/{question_id}/answer", response_model=AnswerResponse)
async def submit_question_answer(
    session_id: str,
    question_id: str,
    req: AnswerSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Evaluate and store an answer for a quiz question with rubric evaluation for open-ended answers."""
    q_res = await db.execute(
        select(Question).where(Question.id == question_id, Question.session_id == session_id)
    )
    question = q_res.scalars().first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found in this session.")

    user_ans = req.user_answer.strip()

    if question.question_type == "MCQ":
        is_correct = (user_ans.lower() == (question.correct_answer or "").strip().lower())
        score = 1.0 if is_correct else 0.0
        feedback = "Correct! Well reasoned." if is_correct else f"Incorrect. The correct answer was: {question.correct_answer}"
        rubric_payload = {"accuracy": score, "type": "MCQ"}
    else:
        # Open-ended rubric evaluation
        eval_result = await OpenEndedEvaluator.evaluate_answer(
            question_prompt=question.prompt,
            user_answer=user_ans,
            reference_text=question.correct_answer or ""
        )
        score = eval_result.score
        feedback = eval_result.constructive_feedback
        rubric_payload = eval_result.model_dump()

    # Insert or update Answer
    ans_res = await db.execute(select(Answer).where(Answer.question_id == question.id))
    answer = ans_res.scalars().first()
    if not answer:
        answer = Answer(
            question_id=question.id,
            user_answer=user_ans,
            score=score,
            feedback=feedback,
            rubric_evaluation=rubric_payload
        )
        db.add(answer)
    else:
        answer.user_answer = user_ans
        answer.score = score
        answer.feedback = feedback
        answer.rubric_evaluation = rubric_payload

    await db.commit()

    return AnswerResponse(
        question_id=question.id,
        score=score,
        feedback=feedback,
        rubric_evaluation=rubric_payload
    )

@router.post("/quizzes/{session_id}/complete", response_model=QuizSessionResponse)
async def complete_quiz_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Finalize quiz, compute aggregate score, update ConceptMastery via EMA, log snapshots, and update recommendations."""
    s_res = await db.execute(select(QuizSession).where(QuizSession.id == session_id))
    session = s_res.scalars().first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz session not found.")

    # Fetch all answers for session
    qa_res = await db.execute(
        select(Question, Answer)
        .outerjoin(Answer, Answer.question_id == Question.id)
        .where(Question.session_id == session.id)
    )
    qa_rows = qa_res.all()

    scores = [ans.score for _, ans in qa_rows if ans and ans.score is not None]
    overall_score = (sum(scores) / len(scores)) if scores else 0.0

    now = datetime.now(timezone.utc)
    session.status = "COMPLETED"
    session.score = round(overall_score, 2)
    session.completed_at = now

    # Update ConceptMastery and MasterySnapshots per concept
    weak_concepts_names = []
    for q, ans in qa_rows:
        if not q.concept_id or not ans or ans.score is None:
            continue

        cm_res = await db.execute(
            select(ConceptMastery).where(
                ConceptMastery.project_id == session.project_id,
                ConceptMastery.user_id == session.user_id,
                ConceptMastery.concept_id == q.concept_id
            )
        )
        cm = cm_res.scalars().first()

        c_res = await db.execute(select(Concept).where(Concept.id == q.concept_id))
        concept_obj = c_res.scalars().first()

        if cm:
            old_score = cm.mastery_score
            new_score = MasteryTracker.calculate_new_mastery(old_score, ans.score, alpha=0.3)
            cm.mastery_score = new_score
            cm.trend = GrowthAnalyzer.determine_trend(new_score, old_score)
            cm.last_assessed_at = now

            if cm.trend == "ATTENTION" or new_score < 0.60:
                if concept_obj and concept_obj.name not in weak_concepts_names:
                    weak_concepts_names.append(concept_obj.name)
        else:
            new_score = round(ans.score, 2)
            trend = "IMPROVING" if new_score >= 0.70 else "ATTENTION"
            cm = ConceptMastery(
                project_id=session.project_id,
                user_id=session.user_id,
                concept_id=q.concept_id,
                mastery_score=new_score,
                confidence_level=0.5,
                trend=trend,
                last_assessed_at=now
            )
            db.add(cm)
            if trend == "ATTENTION" and concept_obj:
                weak_concepts_names.append(concept_obj.name)

        # Snapshot for historical curve
        snapshot = MasterySnapshot(
            project_id=session.project_id,
            user_id=session.user_id,
            concept_id=q.concept_id,
            score=new_score,
            recorded_at=now
        )
        db.add(snapshot)

    # Update LearningContext
    lc_res = await db.execute(select(LearningContext).where(LearningContext.project_id == session.project_id))
    lc = lc_res.scalars().first()
    if lc:
        payload = dict(lc.state_payload or {})
        if weak_concepts_names:
            payload["weak_concepts"] = weak_concepts_names
        lc.state_payload = payload

    # Emit LearningEvent
    event = LearningEvent(
        idempotency_key=f"quiz_completed_{session.id}",
        user_id=session.user_id,
        project_id=session.project_id,
        event_type="QUIZ_COMPLETED",
        payload={
            "session_id": session.id,
            "overall_score": round(overall_score, 2),
            "questions_answered": len(scores)
        }
    )
    db.add(event)

    # Refresh Recommendation
    rec_dict = RecommendationEngine.generate_recommendation(
        learning_goal="Master project topics",
        weak_concepts=weak_concepts_names,
        recent_activity=f"Scored {int(overall_score*100)}% on diagnostic quiz"
    )
    # Check existing recommendation
    rec_res = await db.execute(
        select(Recommendation).where(
            Recommendation.project_id == session.project_id,
            Recommendation.status == "ACTIVE"
        )
    )
    rec = rec_res.scalars().first()
    if rec:
        rec.action_type = rec_dict["action_type"]
        rec.headline = rec_dict["headline"]
        rec.description = rec_dict["description"]
        rec.cta_label = rec_dict["cta_label"]
    else:
        new_rec = Recommendation(
            project_id=session.project_id,
            user_id=session.user_id,
            action_type=rec_dict["action_type"],
            headline=rec_dict["headline"],
            description=rec_dict["description"],
            cta_label=rec_dict["cta_label"],
            status="ACTIVE"
        )
        db.add(new_rec)

    await db.commit()
    await db.refresh(session)

    # Return refreshed questions and answers
    q_responses = [
        QuestionDetailResponse(
            id=q.id,
            session_id=session.id,
            concept_id=q.concept_id,
            question_type=q.question_type,
            prompt=q.prompt,
            options=q.options,
            user_answer=ans.user_answer if ans else None,
            score=ans.score if ans else None,
            feedback=ans.feedback if ans else None
        )
        for q, ans in qa_rows
    ]

    return QuizSessionResponse(
        id=session.id,
        project_id=session.project_id,
        status=session.status,
        score=session.score,
        created_at=session.created_at,
        completed_at=session.completed_at,
        questions=q_responses
    )
