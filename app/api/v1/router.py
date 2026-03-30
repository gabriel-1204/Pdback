from fastapi import APIRouter

from app.domain.feedback.router import router as feedback_router
from app.domain.interview.router import router as interview_router
from app.domain.user.router import router as user_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(interview_router)
v1_router.include_router(feedback_router)
v1_router.include_router(user_router)

