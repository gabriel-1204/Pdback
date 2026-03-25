from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# 1. 회원가입 입력값
class UserRegister(BaseModel):
    """회원가입 입력값 스키마"""
    username: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    position: Literal["backend", "frontend", "fullstack", "data","devops"] | None = None

# 2. 로그인 입력값
class UserLogin(BaseModel):
    """로그인 입력값 스키마"""
    email : EmailStr
    password : str = Field(..., min_length=8)


# 3. 응답값 - 보여줘도되는 값만
class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    username: str
    email: str
    role: Literal["candidate", "admin"]
    is_active: bool
    position: Literal["backend", "frontend", "fullstack", "data","devops"] | None = None
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime

    # MongoDB에서 가져온 데이터를 pydantic 모델로 변환할 때 필요
    model_config = ConfigDict(from_attributes=True)

# 4. 프로필 수정
class UserUpdate(BaseModel):
    """프로필/비밀번호 수정 입력값 스키마"""
    username: str | None = None
    current_password: str | None = None
    new_password: str | None = Field(default=None, min_length=8)
    position: Literal["backend", "frontend", "fullstack", "data","devops"] | None = None

# 5. 비밀번호 재확인(탈퇴 시)
class UserDelete(BaseModel):
    """회원탈퇴 시 비밀번호 재확인 스키마"""
    password: str


# 6. 리프레시 토큰 재발급 요청
class TokenRefresh(BaseModel):
    """리프레시 토큰 재발급 요청 스키마"""
    refresh_token: str

# 7. 토큰 응답값
class TokenResponse(BaseModel):
    """엑세스 토큰, 리프레시 토큰 응답 스키마"""
    access_token: str
    refresh_token: str
