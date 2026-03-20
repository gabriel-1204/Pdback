from pydantic import BaseModel


class QuestionFeedbackResponse(BaseModel):
    """질문별 피드백 응답 — models.QuestionFeedback 대응"""

    question_number: int
    score: float
    comment: str
    model_answer: str


class PostureSummaryResponse(BaseModel):
    """자세/태도 응답 — models.PostureSummary 대응"""

    eyes_score: float
    posture_score: float
    attitude_score: float
    posture_comment: str


class FeedbackRequest(BaseModel):
    """종합 피드백 생성 요청"""

    session_id: str


class FeedbackResponse(BaseModel):
    """종합 피드백 응답 — models.FeedbackDocument 기반"""

    # AI 피드백 점수 (models.AiFeedback 필드명과 통일)
    interview_score: float
    technical_score: float
    logic_score: float
    keyword_score: float

    # AI 피드백 텍스트
    interview_comment: str
    strengths: list[str]
    improvements: list[str]

    # 질문별 개별 피드백 (list[dict] → 구조화된 모델로 변경)
    question_feedbacks: list[QuestionFeedbackResponse]

    # 자세/태도 데이터 (단일 attitude_score → 세분화된 구조로 변경)
    posture_summary: PostureSummaryResponse
