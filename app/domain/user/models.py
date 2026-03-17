from datetime import datetime

from pydantic import BaseModel


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
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    last_login: datetime | None = None

    # AI 면접 관련
    interview_count: int = 0
    position: str | None = None

    # 보안 (JWT)
    refresh_token: str | None = None
