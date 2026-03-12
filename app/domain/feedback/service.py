from app.domain.feedback.schema import FeedbackRequest, FeedbackResponse


async def generate_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """면접 세션의 종합 피드백을 생성합니다."""
    # TODO: MongoDB에서 세션의 전체 Q&A 이력 조회
    # TODO: Gemini API 호출하여 기술적 평가 수행
    # TODO: 태도 점수 집계
    # TODO: 모범 답안 생성
    raise NotImplementedError
