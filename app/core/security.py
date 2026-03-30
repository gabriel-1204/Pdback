#JWT 인증 미들웨어

from datetime import datetime, timedelta, timezone

from jwt import decode, encode
from passlib.context import CryptContext

from app.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

# 비밀번호 해시
# 사용자가 비밀번호 입력하면 변환해서 db에 저장
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """비밀번호 해시화하여 반환"""
    return pwd_context.hash(password)

# 비밀번호 검증
# 사용자가 입력한 비밀번호와 db에 저장된 해시값을 비교해서 맞으면 T, 틀리면 F(bool)
def verify_password(plain: str, hashed: str) -> bool:
    """입력 비밀번호와 DB 해시값 비교하여 일치여부를 반환"""
    return pwd_context.verify(plain, hashed)

# access_token 발급 - 보안상 15,30분으로 설정하는게 일반적, 이후 리프레시 토큰으로 자동연장진행
def create_access_token(data: dict) -> str:
    """엑세스 토큰을 생성하여 반환한다(설정한 유효시간 : 30분)"""
    encode_data = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    encode_data.update({"exp": expire})
    return encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)

# 토큰 검증
def decode_token(token: str) -> dict:
    """토큰을 검증하고 디코딩해서 반환"""
    return decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# 리프레시 토큰
# refresh_token의 경우 보통 7일 ~ 30일 설정
def create_refresh_token(data: dict) -> str:
    """리프레시 토큰을 생성하여 반환(설정한 유효시간 : 7일)"""
    encode_data = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    encode_data.update({"exp": expire})
    return encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)
