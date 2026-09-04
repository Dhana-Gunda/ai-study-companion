from fastapi import APIRouter
from .health import router as health_router
from .sessions import router as sessions_router
from .chat import router as chat_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(sessions_router)
api_router.include_router(chat_router)
