from datetime import datetime

from pydantic import BaseModel, Field


class QuestionFeedback(BaseModel):
    """질문별 개별 피드백 — 기존 list[dict]를 구조화하여 스키마 명확화"""

    question_number: int
    score: float
    comment: str
    model_answer: str


class AiFeedback(BaseModel):
    """AI 피드백 데이터"""

    interview_comment: str
    strengths: list[str]
    improvements: list[str]
    interview_score: float
    technical_score: float
    logic_score: float
    keyword_score: float
    # list[dict] → list[QuestionFeedback]로 구조화: 내부 필드가 불명확했던 문제 해결
    # 이름도 question_model_answer → question_feedbacks로 변경 (실제 역할 반영)
    question_feedbacks: list[QuestionFeedback]


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
    # datetime.now()는 모듈 로드 시 1회만 평가되어 값이 고정되는 버그 → default_factory로 수정
    created_feedback: datetime = Field(default_factory=datetime.now)
