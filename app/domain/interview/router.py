from fastapi import APIRouter

from app.domain.interview.schema import (
    AnswerRequest,
    AnswerResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)
from app.domain.interview.service import start_interview, submit_answer

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/start", response_model=InterviewStartResponse)
async def api_start_interview(request: InterviewStartRequest):
    """면접을 시작하고 첫 번째 질문을 반환합니다."""
    return await start_interview(request)


@router.post("/answer", response_model=AnswerResponse)
async def api_submit_answer(request: AnswerRequest):
    """답변을 제출하고 꼬리 질문을 받습니다."""
    return await submit_answer(request)
