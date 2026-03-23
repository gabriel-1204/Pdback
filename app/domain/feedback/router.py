from fastapi import APIRouter

from app.domain.feedback.schema import FeedbackRequest, FeedbackResponse
from app.domain.feedback.service import create_feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/generate", response_model=FeedbackResponse)
async def api_generate_feedback(request: FeedbackRequest):
    """면접 종료 후 종합 피드백을 생성합니다."""
    return await create_feedback(request.session_id)
