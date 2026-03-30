from fastapi import APIRouter, Depends

from app.domain.interview.schema import (
    AnswerRequest,
    AnswerResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)
from app.domain.interview.service import start_interview, submit_answer
from app.domain.user.dependency import get_current_user

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/start", response_model=InterviewStartResponse)
async def api_start_interview(
    request: InterviewStartRequest,
    user_id: str = Depends(get_current_user)   # 토큰 검증 + user_id 추출
):
    return await start_interview(request, user_id)


@router.post("/answer", response_model=AnswerResponse)
async def api_submit_answer(request: AnswerRequest,
                            user_id: str = Depends(get_current_user)):
    """답변을 제출하고 꼬리 질문을 받습니다."""
    return await submit_answer(request, user_id)
