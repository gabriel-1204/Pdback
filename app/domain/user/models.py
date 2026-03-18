from datetime import datetime

from pydantic import BaseModel, Field


class UserDocument(BaseModel):
    """MongoDB users 컬렉션 문서 스키마"""

    # 기본 정보
    username: str
    email: str
    password_hash: str

    # 권한 / 상태
    role: str = "candidate"
    is_active: bool = True

    # 로그 및 기록
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: datetime | None = None

    # 마이페이지 통계
    interview_count: int = 0
    average_score: float = 0.0
    max_score: float = 0.0

    # 보안 (JWT)
    refresh_token: str | None = None
