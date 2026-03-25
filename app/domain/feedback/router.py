from fastapi import APIRouter, Depends

from app.domain.feedback.schema import (
    FeedbackRequest, FeedbackResponse)
from app.domain.feedback.service import (
    create_feedback, get_feedback, get_history)
from app.domain.user.dependency import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])

# 면접 종료 후 피드백 생성 페이지
# /feedback/generate
@router.post("/generate", response_model=FeedbackResponse)
async def api_generate_feedback(request: FeedbackRequest, current_user: str = Depends(get_current_user)):
    return await create_feedback(request.session_id, current_user)


# history 라우터가 위에 있어야함(history를 interview_id로 착각할수있음)
# 유저별 히스토리 페이지
# /feedback/history
@router.get("/history", response_model=list[FeedbackResponse])
async def api_get_history(current_user: str = Depends(get_current_user)):
    return await get_history(current_user)


# 피드백 상세 페이지 (면접 1건 : 피드백 1건)
# /feedback/{interview_id}
@router.get("/{interview_id}", response_model=FeedbackResponse)
async def api_get_feedback(interview_id: str, current_user: str = Depends(get_current_user)):
    return await get_feedback(interview_id, current_user)

# 모든 라우터들 로그인한 상태에서만 가능하게 막아놓음
# 현재: 본인 피드백/ 히스토리만 열람 가능
# 다른 유저들의 히스토리 열람 가능하게 만드려면 수정해야함
