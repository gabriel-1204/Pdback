from pydantic import BaseModel


class InterviewStartRequest(BaseModel):
    """면접 시작 요청"""
    job_role: str           # 지원 직무 (예: "백엔드 개발자")
    tech_stack: list[str]   # 기술 스택 (예: ["Python", "FastAPI", "Docker"])
    experience_years: int   # 경력 연차 (0 = 신입)


class InterviewStartResponse(BaseModel):
    """면접 시작 응답 - 첫 질문 반환"""
    session_id: str
    question: str


class AnswerRequest(BaseModel):
    """답변 제출 요청"""
    session_id: str
    answer_text: str        # STT로 변환된 답변 텍스트
    attitude_score: float | None = None  # Vision AI 태도 점수 (프론트에서 산출)


class AnswerResponse(BaseModel):
    """답변 제출 응답 - 꼬리 질문 또는 면접 종료"""
    follow_up_question: str | None = None
    is_finished: bool = False
