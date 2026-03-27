from fastapi import APIRouter, Depends, Query

from app.domain.feedback.schema import (
    FeedbackRequest, FeedbackResponse, HistoryResponse, UserStatsResponse)
from app.domain.feedback.service import (
    create_feedback, get_feedback, get_history, get_user_stats)
from app.domain.user.dependency import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])

# /feedback/generate
@router.post("/generate", response_model=FeedbackResponse, status_code=201)
async def api_generate_feedback(request: FeedbackRequest, current_user: str = Depends(get_current_user)):
    """면접 종료 후 피드백 생성 페이지"""
    return await create_feedback(request.session_id, current_user)


# history 라우터가 위에 있어야함(history를 interview_id로 착각할수있음)
# 본인 history만 열람가능 (타인것 X)
# /feedback/history
@router.get("/history", response_model=HistoryResponse)
async def api_get_history(
    page: int = Query(default=1, ge=1),          # 1 이상만 허용
    size: int = Query(default=10, ge=1, le=100), # 1~100만 허용
    current_user: str = Depends(get_current_user)):
    """유저별 히스토리 페이지"""
    return await get_history(current_user, page, size)


# 유선님 마이페이지에서 가져다쓰실 라우터
# /feedback/stats
@router.get("/stats", response_model=UserStatsResponse)
async def api_get_user_stats(current_user: str = Depends(get_current_user)):
    """마이페이지 통계 (총 면접횟수, 평균점수, 최고점수)"""
    return await get_user_stats(current_user)


# 본인 feedback만 열람가능 (타인것 X)
# /feedback/{interview_id}
@router.get("/{interview_id}", response_model=FeedbackResponse)
async def api_get_feedback(interview_id: str, current_user: str = Depends(get_current_user)):
    """피드백 상세 페이지 (면접 1건 : 피드백 1건)"""
    return await get_feedback(interview_id, current_user)
