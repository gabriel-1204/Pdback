from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal


class UserDocument(BaseModel):
    """MongoDB users 컬렉션 문서 스키마"""

    # 기본정보
    username: str = Field(..., min_length=2, description="사용자 이름")
    email: EmailStr = Field(..., description="로그인용 이메일")
    password_hash: str = Field(..., description="bcrypt 암호화된 비밀번호")

    # 권한/상태
    role: str = Field(default="candidate", description="candidate | admin")
    is_active: bool = Field(default=True, description="계정 활성 여부")

    # 로그 및 기록
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: datetime | None = None

    # AI 면접관련
    position: Literal["backend", "frontend", "fullstack", "data","devops"] | None = Field(default=None, description="희망 직무")

    # 보안(JWT)
    refresh_token: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

