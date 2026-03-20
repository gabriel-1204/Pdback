from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# 1. 회원가입 입력값
class UserRegister(BaseModel):
    username: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)

# 2. 로그인 입력값
class UserLogin(BaseModel):
    email : EmailStr
    password : str


# 3. 응답값 - 보여줘도되는 값만
class UserResponse(BaseModel):
    username: str
    email: str
    role: str
    is_active: bool
    position: str | None = None      
    last_login: datetime | None = None  
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True