from app.domain.interview.schema import (
    AnswerRequest,
    AnswerResponse,
    InterviewStartRequest,
    InterviewStartResponse,
)


async def start_interview(request: InterviewStartRequest) -> InterviewStartResponse:
    """면접 세션을 생성하고 첫 질문을 반환합니다."""
    # TODO: Gemini API 호출하여 첫 질문 생성
    # TODO: 세션 정보를 MongoDB에 저장
    raise NotImplementedError


async def submit_answer(request: AnswerRequest) -> AnswerResponse:
    """답변을 분석하고 꼬리 질문을 생성합니다."""
    # TODO: 세션에서 대화 이력 조회
    # TODO: Gemini API 호출하여 꼬리 질문 생성
    # TODO: 답변 및 태도 점수를 MongoDB에 저장
    raise NotImplementedError
