from pydantic import BaseModel


class InterviewStartRequest(BaseModel):
    """면접 시작 요청"""

    job_role: str
    tech_stack: list[str]
    experience_years: int


class InterviewStartResponse(BaseModel):
    """면접 시작 응답 — 첫 질문 반환"""

    session_id: str
    intro_message: str
    question: str


class AnswerRequest(BaseModel):
    """답변 제출 요청"""

    session_id: str
    # models.Answer.answer_content와 이름 통일
    answer_content: str
    # STT 원본 텍스트 (models.Answer.stt_raw_text 대응)
    stt_raw_text: str | None = None


class AnswerResponse(BaseModel):
    """답변 제출 응답 — 꼬리 질문 또는 면접 종료"""

    follow_up_question: str | None = None
    is_finished: bool = False
