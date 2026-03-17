from datetime import datetime

from pydantic import BaseModel, Field


class Answer(BaseModel):
    """질문에 대한 답변"""

    # user_id 삭제: 상위 InterviewDocument에 이미 user_id가 있으므로 중복
    answer_content: str
    # STT 원본 텍스트 추가: answer_content(정제본)와 분리하여 디버깅/정확도 비교용
    stt_raw_text: str | None = None
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    status: str


class Question(BaseModel):
    """면접 질문 (답변 중첩 포함)"""

    # 질문 순번 추가: 꼬리질문 삽입 시 배열 index만으로는 순서 보장이 불안정
    question_number: int
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
    # 면접 전체 소요 시간 추가: 각 질문 duration 합과 별개로 대기시간 포함 전체 세션 시간 기록
    total_duration_seconds: int | None = None
    # datetime.now()는 모듈 로드 시 1회만 평가되어 값이 고정되는 버그 → default_factory로 수정
    created_at: datetime = Field(default_factory=datetime.now)
    finished_at: datetime | None = None
