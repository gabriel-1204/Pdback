from datetime import datetime

from pydantic import BaseModel


class AiFeedback(BaseModel):
    """AI 피드백 데이터"""

    interview_comment: str
    strengths: list[str]
    improvements: list[str]
    interview_score: float
    technical_score: float
    logic_score: float
    keyword_score: float
    question_model_answer: list[dict]


class PostureSummary(BaseModel):
    """자세/태도 데이터 가공 결과"""

    eyes_score: float
    posture_score: float
    bad_posture_count: int
    posture_comment: str


class FeedbackDocument(BaseModel):
    """MongoDB feedbacks 컬렉션 문서 스키마"""

    interview_id: str
    user_id: str
    ai_feedback: AiFeedback
    posture_summary: PostureSummary
    created_feedback: datetime = datetime.now()
