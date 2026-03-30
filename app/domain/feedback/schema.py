from datetime import datetime

from pydantic import BaseModel, ConfigDict


# schema.py: API 요청/응답 모양 (클라이언트한테 보내는 데이터)
class QuestionFeedbackResponse(BaseModel):
    """질문별 피드백 응답 — models.QuestionFeedback 대응"""
    model_config = ConfigDict(protected_namespaces=())

    question_number: int
    score: float
    comment: str             # ai가 내 답변 평가
    model_answer: str        # 모범답안
    question_content: str    # 피드백 페이지에서 (상세보기) 누르면 질문내용 확인가능하게
    answer_content: str      # 피드백 페이지에서 (상세보기) 누르면 내 답변 확인가능하게


class PostureSummaryResponse(BaseModel):
    """자세/태도 응답 — models.PostureSummary 대응"""

    eyes_score: float
    posture_score: float
    attitude_score: float
    posture_comment: str


class HistoryResponse(BaseModel):
    """히스토리 목록 페이지네이션 응답"""

    items: list["FeedbackResponse"]
    total: int   # 전체 피드백 수
    page: int    # 현재 페이지
    size: int    # 페이지당 항목 수


class UserStatsResponse(BaseModel):
    """마이페이지 통계 응답"""

    total_count: int    # 총 면접 횟수
    avg_score: float    # 전체 interview_score 평균
    best_score: float   # 전체 interview_score 최고점
    weekly_count: int   # 이번 주 면접 횟수


class FeedbackRequest(BaseModel):
    """종합 피드백 생성 요청"""

    session_id: str


class FeedbackResponse(BaseModel):
    """종합 피드백 응답 — models.FeedbackDocument 기반"""

    # 면접 메타데이터 (히스토리 목록에서 사용)
    interview_id: str
    position: str
    tech_stack: list[str]
    career_years: int

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

    created_at: datetime
