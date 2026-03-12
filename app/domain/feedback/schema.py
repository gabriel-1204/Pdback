from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    """종합 피드백 생성 요청"""
    session_id: str


class FeedbackResponse(BaseModel):
    """종합 피드백 응답"""
    technical_score: float          # 기술적 정확도 점수 (0~100)
    logic_score: float              # 논리 구성력 점수 (0~100)
    attitude_score: float           # 태도 종합 점수 (0~100)
    overall_score: float            # 종합 점수
    strengths: list[str]            # 잘한 점
    improvements: list[str]         # 개선할 점
    model_answers: list[dict]       # 질문별 모범 답안
    summary: str                    # 총평
