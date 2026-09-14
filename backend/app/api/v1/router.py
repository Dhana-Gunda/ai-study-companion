from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.spaces import router as spaces_router
from app.api.v1.projects import router as projects_router
from app.api.v1.materials import router as materials_router
from app.api.v1.tutor import router as tutor_router
from app.api.v1.quizzes import router as quizzes_router
from app.api.v1.mastery import router as mastery_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

# Register core health probe
api_router.include_router(health_router, tags=["Health"])

# Register domain routers
api_router.include_router(auth_router)
api_router.include_router(spaces_router)
api_router.include_router(projects_router)
api_router.include_router(materials_router)
api_router.include_router(tutor_router)
api_router.include_router(quizzes_router)
api_router.include_router(mastery_router)
api_router.include_router(analytics_router)
api_router.include_router(admin_router)
