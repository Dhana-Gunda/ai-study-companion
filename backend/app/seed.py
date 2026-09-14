import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete

from app.core.database import async_session_maker, init_db
from app.core.security import get_password_hash
from app.models.db_models import (
    User, Space, Project, Concept, ConceptMastery, MasterySnapshot,
    LearningContext, LearningEvent, Recommendation, Conversation, Message
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

def utc_now():
    return datetime.now(timezone.utc)

async def seed_data():
    logger.info("Starting database seeding...")
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Cannot connect to PostgreSQL database: {e}")
        print("\n[ERROR] DATABASE CONNECTION FAILED:")
        print("PostgreSQL at localhost:5432 is currently offline or unreachable.")
        print("Reason: " + str(e))
        print("Please start PostgreSQL (via Docker Desktop: `docker-compose up -d db`)")
        print("or provide a cloud PostgreSQL URL in `backend/.env` (DATABASE_URL=...).\n")
        return False

    async with async_session_maker() as session:
        # 1. Check or create Demo User and Admin User
        result = await session.execute(select(User).where(User.email == "demo@studycompanion.ai"))
        demo_user = result.scalars().first()

        if not demo_user:
            demo_user = User(
                email="demo@studycompanion.ai",
                hashed_password=get_password_hash("password123"),
                name="Demo Learner",
                role="user"
            )
            session.add(demo_user)
            await session.flush()
            logger.info(f"Created demo user: {demo_user.email} (id: {demo_user.id})")
        else:
            logger.info(f"Demo user already exists: {demo_user.email}")

        result_admin = await session.execute(select(User).where(User.email == "admin@studycompanion.ai"))
        admin_user = result_admin.scalars().first()
        if not admin_user:
            admin_user = User(
                email="admin@studycompanion.ai",
                hashed_password=get_password_hash("adminpassword123"),
                name="System Administrator",
                role="admin"
            )
            session.add(admin_user)
            await session.flush()
            logger.info(f"Created admin user: {admin_user.email}")

        # 2. Check or create Space
        result_space = await session.execute(
            select(Space).where(Space.user_id == demo_user.id, Space.name == "Machine Learning")
        )
        space = result_space.scalars().first()
        if not space:
            space = Space(
                user_id=demo_user.id,
                name="Machine Learning",
                description="Mastering machine learning foundations, optimization algorithms, and loss surfaces."
            )
            session.add(space)
            await session.flush()
            logger.info(f"Created space: {space.name} (id: {space.id})")
        else:
            logger.info(f"Space already exists: {space.name}")

        # 3. Check or create Project
        result_proj = await session.execute(
            select(Project).where(Project.space_id == space.id, Project.name == "Intro to ML")
        )
        project = result_proj.scalars().first()
        if not project:
            project = Project(
                space_id=space.id,
                user_id=demo_user.id,
                name="Intro to ML",
                description="Core supervised learning principles, loss surfaces, and gradient descent optimization.",
                learning_goal="Master linear models, loss functions, and gradient descent"
            )
            session.add(project)
            await session.flush()
            logger.info(f"Created project: {project.name} (id: {project.id})")
        else:
            logger.info(f"Project already exists: {project.name}")

        # 4. Concepts, Mastery & Historical Snapshots
        concepts_data = [
            {
                "name": "Linear Regression",
                "description": "Supervised learning algorithm for modeling linear relationships between response and explanatory variables.",
                "score": 0.85,
                "confidence": 0.90,
                "trend": "IMPROVING",
                "history": [0.60, 0.72, 0.85]
            },
            {
                "name": "Cost Functions (MSE)",
                "description": "Mean Squared Error objective function measuring variance between predicted and actual targets.",
                "score": 0.70,
                "confidence": 0.80,
                "trend": "STABLE",
                "history": [0.65, 0.68, 0.70]
            },
            {
                "name": "Gradient Descent",
                "description": "First-order iterative optimization algorithm for finding a local minimum of a differentiable function.",
                "score": 0.45,
                "confidence": 0.50,
                "trend": "ATTENTION",
                "history": [0.50, 0.48, 0.45]
            },
            {
                "name": "Learning Rate Tuning",
                "description": "Hyperparameter controlling the step size at each iteration while navigating towards a minimum.",
                "score": 0.55,
                "confidence": 0.60,
                "trend": "STABLE",
                "history": [0.40, 0.50, 0.55]
            }
        ]

        now = utc_now()
        for cdata in concepts_data:
            result_c = await session.execute(
                select(Concept).where(Concept.project_id == project.id, Concept.name == cdata["name"])
            )
            concept = result_c.scalars().first()
            if not concept:
                concept = Concept(
                    project_id=project.id,
                    name=cdata["name"],
                    description=cdata["description"]
                )
                session.add(concept)
                await session.flush()
                logger.info(f"Created concept: {concept.name}")

                # Create ConceptMastery
                mastery = ConceptMastery(
                    project_id=project.id,
                    user_id=demo_user.id,
                    concept_id=concept.id,
                    mastery_score=cdata["score"],
                    confidence_level=cdata["confidence"],
                    trend=cdata["trend"],
                    last_assessed_at=now
                )
                session.add(mastery)

                # Create Historical Snapshots
                for i, score in enumerate(cdata["history"]):
                    snapshot = MasterySnapshot(
                        project_id=project.id,
                        user_id=demo_user.id,
                        concept_id=concept.id,
                        score=score,
                        recorded_at=now - timedelta(days=(len(cdata["history"]) - 1 - i))
                    )
                    session.add(snapshot)

        # 5. Learning Context
        result_lc = await session.execute(
            select(LearningContext).where(LearningContext.project_id == project.id)
        )
        learning_context = result_lc.scalars().first()
        if not learning_context:
            learning_context = LearningContext(
                project_id=project.id,
                user_id=demo_user.id,
                state_payload={
                    "goals": ["Master linear models, loss functions, and gradient descent"],
                    "strengths": ["Linear Regression formulation", "Matrix multiplication basics"],
                    "weak_concepts": ["Gradient Descent step size calculation", "Learning rate overshoot"],
                    "repeated_mistakes": ["Confusing learning rate with momentum", "Omitting 1/2 factor in MSE derivative"],
                    "summary": "Learner has solid linear model intuition but struggles with gradient calculation and step-size oscillation."
                }
            )
            session.add(learning_context)
            logger.info("Created initial learning context.")

        # 6. Learning Events
        events_data = [
            {
                "key": f"seed_event_proj_created_{project.id}",
                "event_type": "PROJECT_CREATED",
                "payload": {"project_name": project.name, "space_name": space.name}
            },
            {
                "key": f"seed_event_material_uploaded_{project.id}",
                "event_type": "MATERIAL_UPLOADED",
                "payload": {"filename": "intro_to_ml.pdf", "page_count": 18, "chunk_count": 42}
            },
            {
                "key": f"seed_event_quiz_completed_{project.id}",
                "event_type": "QUIZ_COMPLETED",
                "payload": {"score": 0.65, "total_questions": 5, "weakest_concept": "Gradient Descent"}
            }
        ]
        for edata in events_data:
            result_e = await session.execute(
                select(LearningEvent).where(LearningEvent.idempotency_key == edata["key"])
            )
            if not result_e.scalars().first():
                event = LearningEvent(
                    idempotency_key=edata["key"],
                    user_id=demo_user.id,
                    project_id=project.id,
                    event_type=edata["event_type"],
                    payload=edata["payload"]
                )
                session.add(event)

        # 7. Recommendation
        result_rec = await session.execute(
            select(Recommendation).where(Recommendation.project_id == project.id, Recommendation.status == "ACTIVE")
        )
        if not result_rec.scalars().first():
            recommendation = Recommendation(
                project_id=project.id,
                user_id=demo_user.id,
                action_type="PRACTICE_QUIZ",
                headline="Reinforce Gradient Descent & Step Sizing",
                description="Your mastery in Gradient Descent is at 45% (needs attention). Complete a short 3-question adaptive quiz to master convergence criteria.",
                cta_label="Start Diagnostic Quiz",
                status="ACTIVE"
            )
            session.add(recommendation)
            logger.info("Created active recommendation.")

        # 8. Sample Conversation
        result_conv = await session.execute(
            select(Conversation).where(Conversation.project_id == project.id)
        )
        if not result_conv.scalars().first():
            conv = Conversation(
                project_id=project.id,
                user_id=demo_user.id,
                title="Gradient Descent Clarification"
            )
            session.add(conv)
            await session.flush()

            msg1 = Message(
                conversation_id=conv.id,
                role="user",
                content="Why does gradient descent overshoot when the learning rate is too large?",
                tokens_used=18
            )
            msg2 = Message(
                conversation_id=conv.id,
                role="assistant",
                content="When the learning rate is too large, each step exceeds the distance to the local minimum, causing oscillations across the valley and potentially diverging away from the optimal weights [Source: intro_to_ml.pdf — Page 4].",
                sources=[{"filename": "intro_to_ml.pdf", "page_number": 4, "similarity": 0.89}],
                tokens_used=48
            )
            session.add_all([msg1, msg2])
            logger.info("Created sample conversation and messages.")

        await session.commit()
        logger.info("Database seeding successfully completed!")

        # Verification query
        users_count = len((await session.execute(select(User))).scalars().all())
        concepts_count = len((await session.execute(select(Concept))).scalars().all())
        mastery_count = len((await session.execute(select(ConceptMastery))).scalars().all())
        snapshots_count = len((await session.execute(select(MasterySnapshot))).scalars().all())
        events_count = len((await session.execute(select(LearningEvent))).scalars().all())

        print(f"\n--- SEED VERIFICATION ---")
        print(f"Total Users: {users_count}")
        print(f"Total Concepts: {concepts_count}")
        print(f"Total Mastery Records: {mastery_count}")
        print(f"Total Snapshots: {snapshots_count}")
        print(f"Total Learning Events: {events_count}")
        print(f"-------------------------\n")

if __name__ == "__main__":
    asyncio.run(seed_data())
