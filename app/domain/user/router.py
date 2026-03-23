from fastapi import APIRouter, Depends
from app.domain.user import service
from app.domain.user.schemas import UserRegister, UserLogin, UserResponse
from app.domain.user.dependency import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])

#회원가입,로그인은 스키마에서 받기
#회원가입
@router.post("/register", status_code=201)
async def register(data: UserRegister):
    token = await service.register(data.username, data.email, data.password, data.position)
    return {"token":token}

#로그인
@router.post("/login")
async def login(data: UserLogin):
    token = await service.login(data.email, data.password)
    return {"token":token}


#로그아웃, 내정보조회는 이미 로그인한 사용자니까 토큰에서 꺼내서 보기
#로그아웃
@router.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    return await service.logout(current_user)


#내 정보조회
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: str = Depends(get_current_user)):
    return await service.get_me(current_user)
