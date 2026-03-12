from fastapi import APIRouter

from app.domain.feedback.router import router as feedback_router
from app.domain.interview.router import router as interview_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(interview_router)
v1_router.include_router(feedback_router)
