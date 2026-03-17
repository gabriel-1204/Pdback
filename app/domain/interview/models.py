from datetime import datetime

from pydantic import BaseModel


class Answer(BaseModel):
    """질문에 대한 답변"""

    user_id: str
    answer_content: str
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    status: str


class Question(BaseModel):
    """면접 질문 (답변 중첩 포함)"""

    question_content: str
    category: str
    difficulty: str
    expected_duration_seconds: int
    created_by: str
    created_at: datetime
    expected_answer: str
    key_points: list[str]
    answer: Answer | None = None


class InterviewDocument(BaseModel):
    """MongoDB interviews 컬렉션 문서 스키마"""

    # 면접 세션 정보
    user_id: str
    job_role: str
    tech_stack: list[str]
    experience_years: int

    # 질문 목록 (답변 중첩)
    questions: list[Question] = []

    # 메타데이터
    status: str = "in_progress"
    created_at: datetime = datetime.now()
    finished_at: datetime | None = None
