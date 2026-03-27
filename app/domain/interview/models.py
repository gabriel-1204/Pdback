from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.config import KST


class Answer(BaseModel):
    """질문에 대한 답변"""

    answer_content: str
    stt_raw_text: str | None = None
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    status: str


class Question(BaseModel):
    """면접 질문 (답변 중첩 포함)"""
    model_config = ConfigDict(protected_namespaces=())

    question_number: int
    question_content: str
    category: str
    expected_duration_seconds: int
    interviewer: str | None = None
    created_at: datetime
    model_answer: str
    question_keywords: list[str]
    answer: Answer | None = None


class InterviewDocument(BaseModel):
    """MongoDB interviews 컬렉션 문서 스키마"""

    # 면접 세션 정보
    user_id: str
    position: str
    tech_stack: list[str]
    career_years: int

    # 장비 권한
    cam_permit: bool = False
    mic_permit: bool = False

    # 질문 목록 (답변 중첩)
    questions: list[Question] = []

    # 태도/자세 데이터
    eye_contact: int = 0
    posture_safety_rate: int = 0
    cam_status: bool = False
    mic_status: bool = False

    # 메타데이터
    status: str = "in_progress"
    total_duration_seconds: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(KST))
    finished_at: datetime | None = None
