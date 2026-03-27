from fastapi import APIRouter, Depends
from app.domain.user import service
from app.domain.user.dependency import get_current_user
from app.domain.user.schemas import UserDelete, UserLogin, UserRegister, UserResponse, UserUpdate, TokenRefresh, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# 회원가입,로그인은 스키마에서 받기
# 회원가입
@router.post("/register", status_code=201, response_model=TokenResponse)
async def register(data: UserRegister):
    """회원가입 처리"""
    token = await service.register(data.username, data.email, data.password, data.position)
    return token


#로그인
@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """로그인 처리"""
    token = await service.login(data.email, data.password)
    return token



# 로그아웃, 내정보조회는 이미 로그인한 사용자니까 토큰에서 꺼내서 보기
# 로그아웃
@router.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    """로그아웃 처리"""
    return await service.logout(current_user)


# 내 정보조회
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: str = Depends(get_current_user)):
    """현재 로그인한 사용자의 정보를 반환"""
    return await service.get_me(current_user)


# 프로필,비밀번호 수정
@router.patch("/me", response_model=UserResponse)
async def update_me(data:UserUpdate, current_user : str = Depends(get_current_user)):
    """현재 로그인한 사용자의 정보를 수정"""
    return await service.update_me(current_user, data.username, data.position, data.current_password, data.new_password)

# 회원탈퇴
@router.delete("/me")
async def delete_me(data : UserDelete, current_user: str = Depends(get_current_user)):
    """비밀번호 재확인 후 회원탈퇴 처리"""
    return await service.delete_me(current_user, data.password)

# 리프레시토큰
@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: TokenRefresh):
    """리프레시 토큰을 사용하여 새 엑세스 토큰 발급"""
    token = await service.refresh(data.refresh_token)
    return token

# 마이페이지 - 통계 (이번주 면접횟수)
@router.get("/stats/weekly", response_model=dict)
async def get_my_stats(current_user: str = Depends(get_current_user)):
    """마이페이지 통계(이번주 면접횟수)"""
    return await service.get_my_stats(current_user)

# 마이페이지 - 통계 (총 면접횟수, 최고점수, 평균점수)
@router.get("/stats/total", response_model=dict)
async def get_user_stats(current_user: str = Depends(get_current_user)):
    """마이페이지 통계(총 면접횟수, 최고점수, 평균점수)"""
    return await service.get_user_stats(current_user)